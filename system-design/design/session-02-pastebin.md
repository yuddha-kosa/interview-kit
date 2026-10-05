# Session 02 — Pastebin Design
**Date:** 2026-05-10  
**Type:** Mock interview + deep dives  
**Status:** Complete

---

## Problem Statement
Design a Pastebin-like service (like pastebin.com).  
Users can paste text/code, get a short link, share it. Content can be public or private.

**Requirements clarified:**
- 1 million writes/day
- 100 million reads/day (~100:1 read/write ratio)
- Average paste size: 10KB. Hard limit: 1MB
- Access control: public or private (via secret URL)
- Basic rate limiting per user
- Optional URL expiry
- Latency: write < 1s, read < 200ms p99

---

## Key Insight — How Pastebin Differs from URL Shortener

| Dimension | URL Shortener | Pastebin |
|-----------|--------------|----------|
| Data stored | Tiny strings (~200 bytes) | Blobs up to 1MB |
| Storage type | Postgres only | Postgres (metadata) + S3 (content) |
| Read response | 302 redirect | CDN URL for client to fetch content |
| CDN caches | Redirect response | Actual content payload |
| Bandwidth concern | Minimal | Significant |

**Core architectural decision:** Separate metadata from content.
- Postgres → metadata (id, s3 path, expiry, state, access type)
- S3 → actual blob content
- Redis → cache of {short_code: (CDN_URL, expiry, state)}
- CDN → serves actual content to client, backed by S3

---

## Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Write QPS | 1M / 86400 | ~12/sec |
| Read QPS | 100M / 86400 | ~1,158/sec |
| Daily storage | 12 * 86400 * 10KB | ~10 GB/day |
| Annual storage | 10GB * 365 | ~3.6 TB/year |

**Infrastructure conclusions:**
- Postgres: 1 master + 1-2 read replicas (12 writes/sec is trivial)
- Redis: 2 instances (primary + replica for HA). 1,158 ops/sec is well within single instance capacity. Note: capacity depends on machine specs and connection pooling, not just instance count.
- S3: managed, scales automatically
- CDN: managed, scales automatically

---

## System Design

### Architecture
```
Write path:
User → LB → Gateway (auth, rate limit, size check) → App Server
         → S3 (upload blob)
         → Postgres master (store metadata)
         → Redis (cache short_code → CDN URL + expiry)
         → Return 200 + short URL

Read path:
User → LB → Gateway → App Server
         → Redis lookup (short_code → CDN URL + expiry)
         → If hit: validate expiry → return CDN URL
         → If miss: DB read replica → validate expiry → generate CDN URL → update Redis → return CDN URL

Client (separately):
         → CDN URL
         → CDN hit: return content
         → CDN miss: fetch from S3 → cache in CDN → return content
```

**Key design point:** App servers never touch S3 directly. S3 is only ever accessed by CDN. App servers return CDN URLs to clients. Client is responsible for the second fetch leg. Clean two-phase design.

---

## Write Flow Detail

**Order of operations (S3 first):**
```
1. Upload blob to S3 (synchronous)
2. INSERT metadata to Postgres (with state = active)
3. Update Redis cache
4. Return 200 + short URL to user
```

**Why S3 first:**
- If S3 fails → nothing written anywhere → clean 500, no orphaned data
- If Postgres fails after S3 → orphaned S3 object but no URL exposed to user → periodic cleanup job reconciles
- User only gets URL after content is guaranteed retrievable

**Sync vs Async tradeoff:**
- Sync (chosen): simpler consistency, acceptable latency at 12 writes/sec with 10KB payloads (~50-100ms S3 write well within 1s budget)
- Async: better for high throughput or large files. Use status polling API (`GET /api/v1/content/status/{id}`). Inflection point: switch to async if write volume grows 100x or average size grows to MBs.

---

## Schema

```sql
CREATE TABLE pastes (
    id              BIGSERIAL PRIMARY KEY,
    blob_s3_path    TEXT NOT NULL,
    access_type     VARCHAR(10) NOT NULL,  -- 'public' | 'private'
    private_token   VARCHAR(64),           -- only for private pastes
    state           VARCHAR(10) NOT NULL,  -- 'active' | 'expired' | 'failed'
    created_at      TIMESTAMP NOT NULL,
    expires_at      TIMESTAMP
);
```

---

## URL Generation

**Public pastes:** Base62 encode of auto-increment ID (same as URL shortener)
```
id: 100001 → base62 → "q0T" → bit.ly/q0T
```

**Private pastes:** Cryptographically random token
```
16 random bytes → hex → "a3f8c2d1e9b47f3a..."
URL: bit.ly/a3f8c2d1e9b47f3a...
```

**Why random for private:**
- Base62 of sequential ID is guessable (enumerate q0T, q0U, q0V...)
- 16 random bytes = 2^128 possible values → collision probability ~10^-21 at 1B pastes
- Collision handling: UNIQUE constraint on private_token + retry on violation (will never happen in practice)

**Never store short_code** — derive it. Public: encode(id). Private: store token, use as-is.

---

## API Design

### POST /api/v1/content/url
```
Method: POST
Body:   { "content": "..." }

Response 200:
{
  "url": "bit.ly/q0T",
  "expiresAfter": "2027-01-01T00:00:00Z"
}

Status codes:
200 - success
413 - content size exceeds limit (checked at gateway before hitting servers)
500 - internal server error
```

### GET /api/v1/content/path/{short_code}
```
Method: GET

Response 200:
{
  "cdn_url": "https://cdn.example.com/path/to/blob"
}

Status codes:
200 - success, client uses cdn_url to fetch content
404 - short code not found
410 - expired
500 - internal server error
```

### GET https://cdn/path/to/blob  (client fetches directly)
```
Method: GET

Response 200: { "content": "..." }
Response 404: not found
```

---

## Expiry Handling

**On read — lazy expiry:**
```
1. Check expiry timestamp from cache or DB
2. If expired: return 410 immediately (non-blocking)
3. Async: publish "expired:{id}" event to queue
4. Consumer: delete S3 → delete Postgres
5. If consumer fails anywhere: requeue with exponential backoff
```

**Why queue-based:**
- Read path latency unaffected
- Deletion failures don't affect user experience
- Idempotent: S3 delete and Postgres DELETE are both safe to retry

**Idempotency note:**
- S3 delete of already-deleted object: safe
- Postgres `DELETE WHERE id = x` on missing row: returns 0 rows, no error

---

## Private Paste Security

| Layer | Mechanism |
|-------|-----------|
| URL | Cryptographically random unguessable token |
| S3 | Signed URLs (time-limited, prevents direct S3 access) |
| App | Validate access_type on every read request |

**S3 signed URLs:** Generated by app server, time-limited. CDN uses these to fetch from S3. Prevents unauthorized direct S3 access.

---

## Viral Paste — Scaling Analysis

**Scenario:** 10M reads in 1 hour for a single paste = ~2,778/sec (2.4x normal)

**What breaks and where:**

### Layer 1: CDN (first line of defense)
- If paste just went viral, CDN cache is cold across all PoPs
- All PoPs simultaneously miss → thundering herd to origin
- **Fix: CDN Origin Shield** — single designated origin that all CDN PoPs talk to. One request reaches origin, rest wait for CDN to populate. Config, not code.

### Layer 2: Redis
- If Redis is warm (write-through on paste creation): handles spike easily
- If Redis is cold (restart/eviction): all requests hit DB replica simultaneously
- **Fix: Mutex/lock on DB read** — first request acquires lock, fetches from DB, populates cache. All others wait then read from cache.
- Alternative: **Probabilistic early re-expiration** — refresh cache key before it expires, not after.

### Layer 3: S3
- S3 only hit by CDN, never by app servers directly
- CDN origin shield limits S3 requests to one per cache miss
- **Fix: S3 key prefix sharding** — spread objects across prefixes to avoid S3 per-prefix rate limits:
  ```
  /ab/abcdef1234...
  /c3/c3f8a291...
  ```

**Read path reminder:**
```
App server → returns CDN URL (never touches S3)
Client → CDN → (miss) → S3
```
S3 stampede is CDN's problem. App server stampede is Redis/DB's problem. Keep layers separate in your analysis.

---

## What I Got Right This Session

| Decision | Why It's Correct |
|----------|-----------------|
| S3 + Postgres separation | Right tool for right data type |
| Two-phase read (app returns CDN URL, client fetches separately) | App servers never bottleneck on blob transfer |
| Queue-based expiry cleanup | Non-blocking, retriable, idempotent |
| Random token for private pastes | Sequential IDs are enumerable |
| 413 at gateway | Fail fast before wasting backend resources |
| Pushed back on Redis instance count | Reasoning was sound, held ground correctly |
| Caught incorrect stampede analysis | App servers never touch S3 in my design |

---

## What I Got Wrong / Gaps Identified

| Issue | Correct Approach |
|-------|-----------------|
| 7 clarifying questions (max should be 4) | Prioritize top 4, state rest as assumptions |
| Redis replica count math (12 instances vs 2) | Distinguish connections vs instances vs replicas |
| Private paste security (user ID based) | Cryptographically random token, unguessable |

---

## Key Lessons This Session

### 1. Tradeoff articulation is the L6 signal
Don't just pick an approach — state the tradeoff and the inflection point.
> *"I'll go synchronous because at 12 writes/sec it's fine. I'd switch to async if volume grew 100x or size grew to MBs."*

### 2. Hold your ground when reasoning is sound
Pushed back correctly on Redis instance count. Interviewer pushback ≠ you're wrong.
Always reason through it before conceding.

### 3. Restate your design before accepting a critique
If interviewer describes a problem that doesn't exist in your design, correct them:
> *"In my design app servers never touch S3 directly, so that failure mode doesn't apply."*

### 4. Keep layers separate in failure analysis
CDN problems ≠ Redis problems ≠ S3 problems. Each layer has different failure modes and different fixes. Don't mix them.

### 5. Clarifying questions — prioritize ruthlessly
Max 4 questions. Pick the ones that most change your architecture. State the rest as explicit assumptions.

---

## Session Score

| Area | Rating | Notes |
|------|--------|-------|
| Clarifying questions | ⚠️ | Too many (7), prioritization needs work |
| Estimation | ✅ | Correct math, good conclusions |
| Storage architecture | ✅ | S3 + Postgres split, clean separation |
| High level design | ✅ | Two-phase read is elegant |
| API design | ✅ | Clean, correct status codes |
| Failure handling | ✅ | Queue-based expiry, atomic writes |
| Security | ⚠️ | Caught but needed prompting |
| Pushback handling | ✅ | Held ground twice, correctly both times |

**Verdict: Pass at L5. Borderline L6. Gaps are prioritization and proactive security thinking.**

---

## Study Before Session 03

- [ ] Consistency patterns: strong vs eventual vs read-your-writes
- [ ] Think through: what breaks in this design at 100x write volume?
- [ ] Think through: how would you add user accounts and per-user paste history?

---

## Open Questions to Revisit
- How do you handle a paste that's being read while it's being deleted (expiry race condition)?
- How do you enforce per-user rate limiting at the gateway level?
- What's your CDN invalidation strategy when a paste is manually deleted before expiry?
