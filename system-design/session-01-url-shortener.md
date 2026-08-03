# Session 01 — URL Shortener Design
**Date:** 2026-05-10  
**Type:** First mock interview + concept deep dives  
**Status:** Complete

https://miro.com/app/board/uXjVKtqHu1Y=/

---

## Problem Statement
Design a URL shortener like bit.ly.

**Requirements clarified:**
- Core: URL shortening + redirect
- Nice to have: click tracking (count)
- 1000 shortening requests/min (writes)
- 100,000 redirect requests/min (reads) → 100:1 read/write ratio
- Optional URL expiry
- Latency: shortening < 500ms, redirect < 100ms p99

---

## Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Write QPS | 1000/60 | ~16/sec |
| Read QPS | 100,000/60 | ~1600/sec |
| Storage per record | ~500 bytes | — |
| Daily storage | 16 * 86400 * 500B | ~700 MB/day |
| 5-year storage | 700MB * 365 * 5 | ~1.2 TB |

**Conclusion:** Single Postgres master is sufficient for writes. No exotic sharding needed at this scale.

---

## High Level Design

```
User → DNS → CDN → LB → API Gateway → App Servers (multiple instances)
                                            ↓           ↓
                                         Cache      DB Master
                                        (Redis)        ↓
                                                  DB Read Replicas
```

### Write Flow (URL shortening)
```
1. POST /api/v1/url/short {originalURL}
2. App server: INSERT into DB → gets auto-increment ID
3. Encode ID to base62 → short code
4. Update cache: SET short_code → original_url
5. Return {shortURL, expiresAfter}
```

### Read Flow (redirect)
```
1. GET bit.ly/{shortCode}
2. CDN check → HIT: return 302 immediately (never hits origin)
3. CDN MISS → App server
4. Cache lookup → HIT: return 302 + Location header
5. Cache MISS → Read replica lookup
6. Update cache
7. Return 302 + Location: {originalURL}
```

---

## Key Design Decisions

### 1. Short Code Generation — Base62 over Hashing

**Rejected: Hash-based approach (SHA + first N chars)**
- Collision possible → requires resolution loop
- Extra DB lookup needed to check uniqueness
- Complexity: handle collisions, loop retries

**Chosen: Base62 encoded auto-increment ID**
```
DB auto-increment ID: 100001
Base62 encode → "q0T"
Short URL: bit.ly/q0T
```

Why:
- Zero collision possible (IDs are unique by definition)
- No uniqueness check lookup needed
- Single write, no update needed (see below)
- 6 chars = 62^6 = ~56 billion unique URLs

**Base62 character set:**
```
0-9 (10) + a-z (26) + A-Z (26) = 62 chars
```

**Encoding:**
```python
chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(num):
    result = ""
    while num > 0:
        result = chars[num % 62] + result
        num //= 62
    return result

def decode(s):
    result = 0
    for char in s:
        result = result * 62 + chars.index(char)
    return result
```

**Security note:** Sequential IDs are guessable. Mitigation: start counter at large random number (e.g. 1,000,000).

### 2. Single Write — No short_code Column Needed

**Naive (wrong) approach:**
```sql
INSERT → get ID → encode → UPDATE short_code  ← two writes, race condition window
```

**Correct approach — don't store short_code at all:**
```sql
CREATE TABLE urls (
    id        BIGSERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    created_at   TIMESTAMP,
    expires_at   TIMESTAMP
);
```

Since `encode(id)` and `decode(short_code)` are deterministic and reversible:
- Write: INSERT → get ID → encode → return to user. Done. Single write.
- Read: decode(short_code) → id → SELECT WHERE id = ?

No race condition. No update needed. Clean.

**Concurrency:** Postgres BIGSERIAL sequences are atomic. Multiple concurrent inserts each get unique IDs guaranteed.

### 3. Cache Design (Redis)

- **Cache key:** short_code
- **Cache value:** original_url (+ expiry timestamp)
- **Write-through:** Cache updated on every write
- **Read path:** Cache first, DB replica only on miss
- **Setup:** Redis primary + replica for HA (not just load sharing)

**Expected cache hit rate:** Very high (~99%) because:
- All writes populate cache immediately
- Only cold starts or cache restarts cause misses
- Popular URLs (viral links) always in cache

**Capacity:** At 1600 reads/sec, a single Redis instance handles this easily (Redis does 100k+ ops/sec). Two instances for HA.

### 4. URL Expiry

**Rejected: Cron on read replica**  
Problem: replica lag means expired URLs still served after deletion from master.

**Correct approach — Lazy expiry + async cleanup:**
1. Store `expires_at` timestamp in DB
2. On every read (cache hit or miss): check `expires_at`
3. If expired: return 410 Gone, async delete from cache + DB
4. Background job for garbage collection of old rows (not real-time, just cleanup)

Redis TTL can also be set on cache keys for automatic cache-level expiry.

### 5. Click Tracking

**Rejected: Synchronous write in read path**  
Adds latency to redirect (latency-sensitive operation).

**Correct approach — Async via message queue:**
```
Redirect request
    → return 302 immediately (user gets redirect fast)
    → publish click event to Kafka/SQS (non-blocking)
        → Analytics consumer reads events
        → Writes to Analytics DB (separate from main DB)
```

Analytics DB is separate because:
- Different access pattern: append-heavy writes + aggregation queries
- Failure in analytics must never affect redirect latency
- Can be eventually consistent (counts don't need to be real-time)

### 6. CDN

- DNS for bit.ly resolves to CDN IP, not origin servers
- Popular short URLs cached at CDN edge (PoPs globally)
- Cache HIT at CDN: redirect served in 5-10ms, origin never touched
- Cache MISS: CDN forwards to origin, caches response
- 301 vs 302 affects CDN caching aggressiveness

1. User requests bit.ly/B8aZ3
2. DNS resolves bit.ly to CDN's IP (not your server's IP)
3. Request hits nearest CDN Point of Presence (PoP)
4. CDN checks its cache:
   a. Cache HIT → returns 302 + Location header directly. 
      Your servers never touched.
   b. Cache MISS → CDN forwards to your origin server,
      gets response, caches it, returns to user

**When CDN helps:** Popular/viral URLs (majority of traffic)  
**When CDN doesn't help:** Write requests, unique one-time URLs

---

## API Design

### POST /api/v1/url/short
```
Method: POST
Body:   { "originalURL": "https://..." }

Response 200:
{
  "shortURL": "bit.ly/q0T",
  "expiresAfter": "2027-01-01T00:00:00Z"
}

Response codes: 200, 400, 500
```

### GET /{shortCode}  (redirect)
```
Method: GET
No body.

Response 302:
  Location: https://original-long-url.com/...

Response 410: Gone (expired URL)
Response 404: Not found
```

---

## HTTP — Key Concepts (Gap Identified This Session)

| Code | Meaning | Use case |
|------|---------|----------|
| 200 | OK | Successful GET |
| 201 | Created | Resource created (e.g. POST /url/short success) |
| 301 | Permanent Redirect | Browser + CDN cache forever. Lose click tracking. |
| 302 | Temporary Redirect | Browser doesn't cache. Use for bit.ly (need tracking). |
| 400 | Bad Request | Invalid input |
| 404 | Not Found | Short code doesn't exist |
| 410 | Gone | Short code existed but expired |
| 500 | Internal Server Error | Server-side failure |

**How redirect works:**
Server returns `302 + Location: https://destination.com` header.  
Browser reads Location header and navigates. Server does NOT proxy traffic.

---

## What I Got Wrong This Session

| Mistake | Correct Answer |
|---------|---------------|
| Used 201 for redirect response | 302 (temporary) or 301 (permanent) |
| Hash-based short code generation | Base62 auto-increment |
| Two-write approach for short_code | Don't store short_code — derive from ID |
| Cron on read replica for expiry | Lazy expiry + async cleanup |
| "Subprocess" for click tracking | Kafka event → analytics consumer |
| Jumped to impl before drawing system | Always: boxes first, then deep dive |

---

## Gaps to Study Before Session 02

- [ ] HTTP status code families (2xx, 3xx, 4xx, 5xx) — know top 15 cold
- [ ] How HTTP redirects work (301 vs 302 vs 307 vs 308)
- [ ] DNS resolution — full flow from browser to server
- [ ] TCP handshake basics
- [ ] Redo diagram: add CDN, proper cache cluster, multiple app servers

---

## Session Score

| Area | Rating |
|------|--------|
| Clarifying questions | ✅ Good |
| Estimation | ✅ Strong |
| High level design | ⚠️ Incomplete |
| API design | ⚠️ Defined late, missing initially |
| Deep dive | ⚠️ Partial |
| HTTP fundamentals | ❌ Gap |
| Communication structure | ⚠️ Needs work |

**Overall: Not a pass yet. Strong foundation. All gaps are fixable.**

---

## Next Session
- Mock: same URL shortener, full 45-min run, scored properly
- Or: new problem after HTTP gaps are studied
- Topic: DNS + CDN deep dive
