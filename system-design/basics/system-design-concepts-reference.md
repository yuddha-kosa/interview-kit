# System Design Concepts Reference
**Last Updated:** 2026-05-10  
**Source:** Study sessions 01-02

---

## 1. HTTP Fundamentals

### Status Code Families
| Family | Meaning |
|--------|---------|
| 2xx | Success |
| 3xx | Redirect |
| 4xx | Client error |
| 5xx | Server error |

### Most Important Status Codes
| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET |
| 201 | Created | Resource created (POST success) |
| 202 | Accepted | Async request accepted, not yet processed |
| 301 | Permanent Redirect | Browser + CDN cache forever. Loses click tracking. |
| 302 | Temporary Redirect | Browser doesn't cache. Use for bit.ly (need tracking). |
| 400 | Bad Request | Invalid input from client |
| 404 | Not Found | Resource doesn't exist |
| 410 | Gone | Resource existed but permanently deleted/expired |
| 413 | Payload Too Large | Content size exceeds limit. Check at gateway. |
| 503 | Service Unavailable | System overloaded, load shedding in effect |

### How HTTP Redirect Works
```
Server returns:
  HTTP/1.1 302 Found
  Location: https://original-url.com/path

Browser reads Location header and navigates.
Server does NOT proxy traffic. Client does the redirect.
```

### 301 vs 302 — Key Difference
```
301 → browser caches permanently → subsequent requests bypass your servers
     → lose click tracking
     → use when destination never changes

302 → browser does not cache → every click hits your servers
     → can track clicks
     → use for URL shorteners, A/B testing, temporary redirects
```

---

## 2. DNS Resolution

### Full Resolution Flow
```
1. Browser cache          → check if IP already cached locally
2. OS cache               → check /etc/hosts and OS DNS cache
3. Router/ISP DNS cache   → check local network resolver
4. Recursive DNS resolver → ISP's resolver, checks its cache
5. Root nameserver        → knows TLD nameservers (.com, .ly, .io)
6. TLD nameserver         → knows authoritative nameserver for domain
7. Authoritative nameserver → returns actual IP for the domain
8. IP returned to browser → browser connects to that IP
```

### Key Points
- Each layer has its own cache — most lookups resolve at layer 2-4
- Full resolution (all 7 hops) is rare, takes 20-120ms
- Cached resolution: sub-millisecond
- DNS for bit.ly resolves to CDN IP, not origin server IP
- TTL on DNS records controls how long each layer caches

---

## 3. TCP Handshake

### Three-Way Handshake
```
Client  →  SYN        →  Server   (I want to connect)
Client  ←  SYN-ACK    ←  Server   (OK, I'm ready)
Client  →  ACK        →  Server   (Great, let's go)
← now HTTP request can be sent →
```

### Why It Matters for System Design
- Every NEW TCP connection costs 1 RTT before data flows
- TLS adds another 1-2 RTTs on top (TLS handshake)
- Total: 2-3 RTTs before first byte of actual request

### Implications
```
CDN matters → CDN PoP is 5ms RTT vs 200ms to origin
              saves 2-3 RTTs * 195ms = significant latency reduction

HTTP/2 → multiplexes multiple requests over single TCP connection
         reuses connection → avoids repeated handshakes

Connection pooling → reuse existing TCP connections
                     critical for DB connections especially
```

---

## 4. Redis Data Structures

### String (default)
```
SET key value
GET key → value
INCR counter → atomic increment
```
Use for: session cache, simple object cache, distributed counters

### Hash (nested object)
```
HSET user:123 name "John" age 30
HGET user:123 name → "John"
HGETALL user:123 → all fields
HSET user:123 age 31  ← update single field without fetching whole object
```
Use for: user profiles, object metadata, config storage
Advantage: update one field without deserializing entire object

### List (ordered, queue)
```
RPUSH feed event1 event2   ← push to right
LPOP feed → event1          ← pop from left (FIFO queue)
LRANGE feed 0 9 → 10 items  ← range query
```
Use for: activity feeds, message queues, recent items

### Set (unique members, unordered)
```
SADD user:123:friends "alice" "bob"
SISMEMBER user:123:friends "alice" → 1
SINTER user:123:friends user:456:friends → mutual friends
SUNION → all friends combined
```
Use for: unique visitors, tags, friend lists, set operations

### Sorted Set (unique members WITH score)
```
ZADD leaderboard 1500 "player:alice"
ZADD leaderboard 3200 "player:bob"
ZRANGE leaderboard 0 9 WITHSCORES REV → top 10
ZINCRBY leaderboard 100 "player:alice" → atomic score increment
ZREMRANGEBYSCORE → remove by score range (sliding window rate limiter)
```
Use for: leaderboards, trending content, rate limiting, priority queues, timelines

### Rule of Thumb
```
If you find yourself doing:
  GET → deserialize → sort/filter/count → serialize → SET
STOP. Redis has a native data structure for this.

Ask: "What operations do I need on this data?"
Then pick the data structure that supports those operations natively.
```

---

## 5. Distributed Locks

### The Problem
```
Process A: GET lock → nil (free)
                           ← Process B: GET lock → nil (free)
Process A: SET lock "A"
                           ← Process B: SET lock "B"  ← overwrites A!
Both think they have the lock → race condition
```

### Redis Solution — SET NX EX (atomic)
```
SET lock_key "processA_token" NX EX 30

NX  → only set if Not eXists
EX  → expire in 30 seconds
Single command → atomic, no race condition window
```

### The Expiry Problem
```
Process A acquires lock (EX 30s)
Process A's work takes 45s
At t=30: lock expires
Process B acquires lock
At t=45: Process A finishes, releases lock → deletes Process B's lock!
```

### Fix — Unique Token + Lua Script
```python
# Acquire
token = uuid4()
SET lock_key {token} NX EX 30

# Release — verify ownership before delete
Lua script (atomic):
  if GET lock_key == token:
      DEL lock_key
  else:
      return 0  # someone else owns it, don't delete
```

### Zookeeper — Ephemeral Nodes
```
Process A creates ephemeral node /locks/resource
→ node tied to Process A's session
→ Process A crashes → session dies → node auto-deleted
→ No TTL needed, no token verification needed
→ Process B: create same node → success (lock acquired)
```

### Lock Best Practices
```
1. Centralize lock management — one service/library, not scattered across codebase
2. Consistent lock ordering — always acquire locks in same order to prevent deadlock
   Bad:  Service A locks user→inventory, Service B locks inventory→user → deadlock
   Good: Both always lock user first, then inventory → deadlock impossible
3. Keep lock scope small — acquire late, release early
4. Always use timeouts — never wait indefinitely
5. Avoid holding locks during external calls (API calls, user input, etc.)
```

### Redis vs Zookeeper
| | Redis | Zookeeper |
|--|-------|-----------|
| Mechanism | TTL + unique token | Ephemeral node + session |
| Cross-delete risk | Yes, needs token check | No, sessions own nodes |
| Crash recovery | TTL expiry (fixed time) | Immediate on session death |
| Infrastructure | Lightweight | Heavy, complex cluster |
| Latency | Sub-millisecond | Higher (consensus protocol) |
| Use case | High throughput locking | Strong coordination, leader election |

---

## 6. Two-Phase Commit (2PC)

### The Problem
Atomic operation spanning multiple independent systems:
```
Debit Bank A + Credit Bank B
Must both succeed or both fail
Can't use single ACID transaction (different systems)
```

### The Two Phases

**Phase 1 — Prepare (Voting)**
```
Coordinator → all participants: "Can you do this? Don't commit yet."
Each participant:
  - Checks if it CAN do the operation
  - Acquires locks
  - Writes to WAL (write-ahead log)
  - Votes YES or NO
After YES vote: participant is committed to completing if told to
```

**Phase 2 — Commit or Abort**
```
All YES → Coordinator sends COMMIT to all → all execute + release locks
Any NO  → Coordinator sends ABORT to all → all rollback + release locks
```

### Problems with 2PC
```
1. Blocking protocol
   Participants hold locks after voting YES, waiting for coordinator
   If coordinator crashes → participants blocked indefinitely

2. Coordinator is SPOF
   Coordinator crashes after committing participant A but before B
   → A committed, B didn't → inconsistent state
   Fix: replicated coordinator using Raft/Paxos

3. Latency
   Minimum 2 network round trips before anything commits
   Expensive at high throughput
```

### When to Use 2PC
```
✓ Strong consistency non-negotiable
✓ Financial transactions
✓ Small number of participants
✓ Low throughput acceptable
```

---

## 7. Saga Pattern

### The Idea
Instead of locking everything upfront, execute steps sequentially.
If any step fails, run compensating transactions to undo previous steps.

### Example — Order Flow
```
Normal flow:
  Reserve inventory → Charge payment → Send email → Done ✓

Failure flow (payment fails):
  Reserve inventory → Charge payment FAILS
  → Compensating: Release inventory reservation
  → Return error to user ✓
```

### Key Rules
```
1. Every step must have a compensating transaction
2. Irreversible steps go LAST
   Bad:  Charge payment → Reserve inventory → Send email
   Good: Reserve inventory → Send email → Charge payment (last, irreversible)

3. Steps must be idempotent (safe to retry)
4. Compensating transactions must also be idempotent
```

### 2PC vs Saga
| | 2PC | Saga |
|--|-----|------|
| Atomicity | Strong (all or nothing) | Eventual (compensating) |
| Locks held | Across entire transaction | Only during each local step |
| Latency | High (2 round trips) | Lower (async steps) |
| Throughput | Low | High |
| Complexity | Protocol complexity | Compensating logic complexity |
| Use case | Strong consistency required | High throughput, eventual consistency ok |

---

## 8. Load Shedding

### Definition
Deliberately dropping requests when system is overwhelmed to prevent total collapse.

**Core principle:** Serving 20% of requests well is better than crashing and serving 0%.

### Without Load Shedding — Collapse Scenario
```
5x normal traffic arrives
All requests accepted → queue grows
Memory fills → latency spikes 100ms → 1s → 10s → timeout
DB connection pool exhausted
Cascading failures across services
System crashes → 0 requests served
Recovery: minutes to hours
```

### With Load Shedding
```
5x normal traffic arrives
System detects overload
Drops 80% of requests with 503
Serves 20% at full quality
System stays healthy
Recovery: automatic when traffic drops
```

### Priority Order — What to Shed First
```
Shed last (highest priority):
  → Payment processing, authentication, core writes

Shed early (lower priority):
  → Analytics collection, reporting, non-critical reads

Shed first (lowest priority):
  → Batch jobs, background tasks, nice-to-have features
```

### Overload Detection Signals
```
- CPU > 80%
- Memory > 85%
- Request queue depth > threshold
- Response latency > SLO target
- Error rate rising
- Connection pool near exhaustion
```

### Implementation Patterns
```
1. Queue with max depth
   Requests → Queue (max N) → Workers
   Queue full → reject with 503

2. Token bucket
   System has N tokens, each request costs 1
   No tokens → shed request
   Tokens replenish at fixed rate

3. Adaptive concurrency limit
   Measure latency continuously
   Latency rising → reduce concurrency limit
   Netflix Concurrency Limits library

4. CPU/memory threshold
   if cpu > 80%: probabilistically reject requests
```

### Where to Implement
```
API Gateway  ← best place, shed before consuming backend resources
App Servers  ← second line of defense
DB           ← connection pool limit is implicit load shedding
```

### vs Related Concepts
```
Rate Limiting  → per client, proactive, "you get 100 req/min"
Load Shedding  → global, reactive, "system at capacity, dropping requests"
Circuit Breaker → stops calls to failing downstream service
Throttling     → slows processing, makes requests wait
```

---

## 9. Event Sourcing

### Traditional — Store Current State
```
orders table:
id: 123, status: "shipped", amount: 100
← only know current state, history lost
```

### Event Sourcing — Store What Happened
```
events table:
1. OrderPlaced    {orderId: 123, amount: 100, at: t1}
2. PaymentCharged {orderId: 123, amount: 100, at: t2}
3. OrderShipped   {orderId: 123, trackingId: xyz, at: t3}

Current state = replay all events
```

### Key Properties
```
- Events are immutable facts — never update or delete, only append
- Current state derived by replaying events
- Can reconstruct any past state (replay up to point in time)
- Full audit trail preserved
- Natural fit for event-driven/Kafka architectures
```

### Downside + Fix
```
Problem: replaying all events gets slow as they accumulate

Fix: Snapshots
  → periodically save current state as snapshot
  → only replay events after last snapshot
```

### When to Use
```
✓ Audit trail required (financial, compliance, healthcare)
✓ Need to reconstruct past state (debugging, analytics)
✓ Event-driven microservices architecture
✓ CQRS pattern (separate read and write models)

✗ Simple CRUD with no history requirements
✗ High write throughput with large event payloads
```

---

## 10. Workflow Engines (Temporal / Step Functions / Conductor)

### The Problem They Solve
Multi-step business processes where:
- Steps can fail and need retry
- System can crash mid-flow
- Need to know exactly where you are
- Some steps run in parallel, some sequential
- Need visibility into stuck/failed workflows

### What They Give You
```
✓ State persistence     → knows exactly which step you're on
✓ Automatic retries     → configurable retry + backoff per step
✓ Failure recovery      → crash → resume from last completed step
✓ Timeouts              → step too slow → fail and retry
✓ Visibility            → dashboard showing all workflow states
✓ Versioning            → deploy new code without breaking running workflows
✗ Automatic rollback    → does NOT undo side effects of completed steps
✗ Data consistency      → does NOT manage DB state across steps
```

### Critical Limitation — No Automatic Rollback
```
Worker A runs → updates DB state → SUCCESS
Worker B runs → FAILS after all retries
Workflow: FAILED

DB state from Worker A: stuck in transient state forever
Orchestrator cannot undo what Worker A did
Manual intervention or compensating logic required
```

### Orchestrator + Saga = Complete Pattern
```
Orchestrator handles: workflow coordination, retries, visibility
Saga handles:         data consistency, compensating transactions

Use both together when steps have stateful side effects.
Orchestrator alone is sufficient only when steps are stateless/idempotent.
```

### State Machine Best Practice
```
Every transient state needs an exit — forward OR backward:

Device states:
Registered → Provisioning → Ready        (forward)
Provisioning → Failed                    (failure exit)
Provisioning → Registered                (rollback exit)

Never leave a state with no exit path.
```

### Tools
```
Temporal         → code-first, strong consistency guarantees
AWS Step Functions → JSON state machine, managed service, Lambda integration
Netflix Conductor → open source, used at Netflix and RapidAI
Apache Airflow   → DAG-based, primarily data pipelines
```

---

## 11. Caching Patterns

### Cache-Aside (Lazy Loading)
```
Read:
  1. Check cache
  2. Hit → return data
  3. Miss → read from DB → update cache → return data

Write:
  1. Write to DB
  2. Invalidate or update cache
```
Use when: read-heavy, cache misses are acceptable, data changes infrequently

### Write-Through
```
Write:
  1. Write to cache
  2. Write to DB synchronously
  3. Return success

Read:
  1. Always check cache first (should always hit)
```
Use when: write latency acceptable, need cache always warm

### Write-Behind (Write-Back)
```
Write:
  1. Write to cache
  2. Return success immediately
  3. Async: write to DB later (batched)
```
Use when: write throughput critical, eventual DB consistency acceptable
Risk: data loss if cache fails before async write

### Cache Eviction Policies
```
LRU  (Least Recently Used)  → evict item not accessed longest
LFU  (Least Frequently Used) → evict item accessed fewest times
TTL  (Time To Live)          → evict after fixed time period
FIFO (First In First Out)    → evict oldest inserted item
```

---

## 12. CDN (Content Delivery Network)

### How It Works
```
Without CDN:
  User in Mumbai → 200ms → Origin in US-East

With CDN:
  User in Mumbai → 5ms → CDN PoP in Mumbai → cached content
  CDN miss → CDN fetches from origin → caches → serves user
```

### CDN Cache Hit vs Miss
```
HIT:  CDN serves content directly, origin never touched
MISS: CDN forwards to origin, gets response, caches it, serves user
```

### What Gets Cached
```
URL shortener: 302 + Location header
Pastebin:      actual content payload
Static assets: JS, CSS, images
API responses: if cacheable (GET, public data)
```

### CDN Origin Shield
```
Without origin shield:
  100 CDN PoPs all miss simultaneously → 100 requests hit origin

With origin shield:
  100 CDN PoPs miss → all route to single origin shield PoP
  → 1 request hits origin → response cached → 100 PoPs served
```
Use for: protecting origin from thundering herd during cold cache

### 301 vs 302 and CDN
```
301 → CDN caches aggressively (permanent)
302 → CDN respects as temporary, shorter TTL or no cache
```

---

## Key Interview Phrases

**On tradeoffs:**
> "I'll go with X because at current scale Y is acceptable. 
>  The inflection point where I'd switch to Z is when [condition]."

**On holding ground:**
> Reason through the challenge before conceding.
> Interviewer pushback ≠ you're wrong.

**On restating design:**
> "Just to clarify — in my design [component] never touches [other component] 
>  directly, so that failure mode doesn't apply here."

**On proactive failure analysis:**
> "What breaks first in this design? At what order of magnitude does it fall over?"

**On orchestrators:**
> "I'd use Temporal for workflow coordination, but since steps have stateful 
>  side effects I'd implement Saga with compensating transactions. 
>  Every transient DB state has an explicit failure exit."
