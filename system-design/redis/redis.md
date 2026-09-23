# Architectural Master Notes: The Redis Engine & Distributed Lifecycle

Redis (Remote Dictionary Server) is an open-source, in-memory, key-value data structure store used widely as a database, cache, message broker, and streaming engine. Unlike disk-bound databases that process transactions by loading blocks to memory, Redis holds its entire active data corpus directly inside RAM, performing mutations via a highly optimized single-threaded event loop.

---

## 1. The Core Engine Architecture: Single-Threaded Event Loop

A primary question in system design interviews is: "How does Redis handle over 100,000 requests per second if it is single-threaded?"

### The Performance Multipliers

* **Zero Lock Contention:** Because exactly one thread mutates data in RAM, Redis completely avoids the CPU overhead of thread context-switching, thread synchronization, mutex locks, and deadlocks.
* **I/O Multiplexing (epoll/kqueue):** Redis uses an event loop backed by non-blocking sockets. A single thread handles thousands of client connections simultaneously by monitoring multiplexed network events, picking up completed socket payloads, executing them instantly in RAM, and streaming them back out.

### The Architectural Limitation: Blocking Commands

Because a single thread handles all requests sequentially, any command with a time complexity of O(N) will block the entire database server node, causing incoming client requests to pile up and timeout.

* **The Antipattern:** Running `KEYS *` (which scans the entire keyspace) or calling `DEL` on a collection with millions of items in a production environment.
* **The Production Fix:** Use `SCAN` instead of `KEYS` to yield pieces of the dataset iteratively. For large deletions, use `UNLINK` instead of `DEL` — this unlinks the key instantly from the cluster namespace in O(1) and delegates the heavy memory reclamation workload to an asynchronous background worker thread.

> **Note:** Since Redis 6.0, optional I/O threads can parallelize the network read/write layer (parsing input, writing output buffers), but command *execution* against the keyspace remains strictly single-threaded. This nuance is worth stating explicitly if an interviewer pushes on "is Redis really single-threaded?"

---

## 2. Key Namespacing & Formatting Standards

Redis maintains a flat, multi-tenant entry keyspace. To emulate an organized schema, production-grade systems enforce strict colon-based key serialization patterns:

```
domain_scope:subdomain/collection:unique_identifier
```

**Example Scenarios:**

* `user:profile:1001` → Stores string-serialized user metadata profiles.
* `session:tokens:user_1001` → Maps to an active session security token hash.
* `feed:region:us-west-2` → Points to a specialized regional chronological timeline index.

---

## 3. Data Structures: Deep Dive & Use Cases

### A. Strings (Key-Value)

The fundamental primitive. Stores raw strings, compressed JSON string blocks, or integers up to 512MB.

* **Under the Hood:** Backed by SDS (Simple Dynamic String) structures that store string length explicitly, guaranteeing O(1) length checks and preventing buffer overflows.
* **Commands:** `SET`, `GET`, `INCR` (atomic integer increment).
* **System Design Scenario (URL Shortener):** Managing a global sequential atomic counter via `INCR global_url_counter` to generate clean, collision-free values before compressing them into a Base62 token.

### B. Hashes (Key-Map / Dictionaries)

An internal map of fields to values inside a single overarching main cluster key.

* **Under the Hood:** Automatically switches from a space-saving memory allocation layout (Listpack/ZipList) to an open-chained Hashtable as the number of sub-fields grows.
* **Commands:** `HSET`, `HGET`, `HDEL`, `HINCRBY`.
* **System Design Scenario (Session Management):** Storing user session states (device info, login status). Using `HSET session:99x status "ACTIVE"` allows the app server to update or fetch specific parameters without serialization network bottlenecks.

### C. Lists (Linked Lists)

A sequentially ordered sequence of strings.

* **Under the Hood:** Configured via a Quicklist (a doubly-linked list of compact array chunks) ensuring insertion/deletion at endpoints takes O(1) time regardless of scale.
* **Commands:** `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LRANGE`.
* **System Design Scenario (Task Queuing):** Managing an asynchronous task runner background queue. Producers use `RPUSH task_queue job_data`, and consumers execute atomic blocking point lookups via `LPOP` or `BLPOP` to ingest tasks linearly.

### D. Sorted Sets (ZSET)

A unique collection of string elements where every member is paired with a numeric score.

* **Under the Hood:** Dual-allocated using a Hashtable (for O(1) element lookups) paired with a Skip List (to keep elements sorted by score in O(log N) insertion/search bounds).
* **Commands:** `ZADD`, `ZREVRANGEBYSCORE`, `ZRANGEBYSCORE`.
* **System Design Scenario (Infinite Feed Scroll Pagination):** Building a news feed timeline by setting `Score = Epoch Timestamp`.

```
[ REDIS ZSET TIMELINE IN RAM ]
+------------------------------------+
9:05 PM| NEWS#105 (Breaking)  Score: 090500 | <- Ignored! (Newer than cursor)
9:05 PM| NEWS#104 (Breaking)  Score: 090500 |
+------------------------------------+
| ======= USER'S CURSOR: 09:00:00 ===|
+------------------------------------+
8:59 PM| NEWS#011             Score: 085900 | <- Infinite scroll page 2 starts here!
8:58 PM| NEWS#010             Score: 085800 |
+------------------------------------+
```

**The Cursor Fix:** When a user scrolls to the bottom of Page 1, the backend extracts the timestamp score of the oldest article returned (e.g., `09:00:00`) and treats it as the cursor. Page 2 executes `ZREVRANGEBYSCORE feed:region:US 09:00:00 -inf LIMIT 0 10`. Even if breaking news arrives at 09:05:00 mid-scroll, it is automatically skipped. This prevents the "drifting feed" duplication anomaly seen in basic list arrays.

---

## 4. Distributed Locking (The Fencing Token Pattern)

To safely restrict concurrent workers across a cluster from manipulating the same resource (e.g., purchasing the final available airline seat), you implement a pessimistic lock.

### Step 1: Acquisition Strategy (SET NX PX)

The acquiring API worker node must issue a single atomic write command to Redis:

```
SET lock:seat_42 "unique_uuid_A" NX PX 30000
```

* `lock:seat_42`: The predictable key name. It must be identical across all servers so they collide on the exact same mutex memory address.
* `"unique_uuid_A"`: The lock value — a unique token generated by this specific worker thread (like a UUID). It serves as a **fencing token**.
* `NX`: Instructs Redis to write only if the key does not already exist.
* `PX 30000`: Sets a 30-second TTL expiry. If the worker server loses power mid-operation, the lock automatically clears, avoiding permanent system deadlocks.

### Step 2: Release Strategy (Atomic Lua Script)

If a worker hits a database lag wall, its operation could take 32 seconds. At second 30, its lock expires, and Server B acquires it. If Server A finishes at second 32 and issues a blind `DEL lock:seat_42`, it will inadvertently vaporize Server B's active lock.

To block this, servers must execute an atomic Lua script inside Redis to compare values before deletion:

```lua
-- Atomic script validation inside Redis RAM
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0 -- Val mismatch: lock was lost, abort delete safely
end
```

> **Interview follow-up:** this single-node lock pattern is not safe against a Redis primary failover mid-lock (the lock write may not have replicated to the new primary yet, letting two clients hold it simultaneously). The proposed fix for multi-node safety is **Redlock** (acquire the lock against a majority of independent Redis masters) — controversial in the distributed-systems community (Kleppmann's critique vs. Redis's response), but worth naming if asked "is this safe across a cluster?"

---

## 5. Distributed Horizontal Scaling: Consistent Hashing (Client-Side)

When data scale outgrows a single machine's RAM footprint, you partition data across multiple Redis servers. To scale elastic cluster environments without triggering massive invalidation storms, use consistent hashing.

### The Clockwise Search Mechanics

Both physical servers and incoming keys are routed onto a virtual circle (the hashing ring) mapping from 0 to 2³²-1.

```
                --- POSITION 0 ---
           /                          \
    [redis-node-1]              [redis-node-2]
    (Hash Position: 50,000)     (Hash Position: 2,000,000)

         |                             |
         |       User's Key Hashes     |
         |       to: 1,500,000         |
         +=========>  (X)              |
                       |               |
                       +--Clockwise--> v
                                [redis-node-2] Wins!
```

When you request `feed:region:us-west-2`, your application routing proxy runs a deterministic local string hash (e.g., MurmurHash3) to derive a location on the circle (e.g., position 1,500,000). It sweeps clockwise along the ring until it hits the first registered Redis server node instance (`redis-node-2` at 2,000,000) and extracts its specific network connection parameters.

**Location of the ring configuration:** The ring configuration data structure is kept entirely in the local RAM memory of the application server instances (or an inline routing tier proxy like Twemproxy). It takes zero external network hops to calculate target server destinations.

This is the **client-side** approach to partitioning. Contrast it with Redis's own native clustering in §9 below.

---

## 6. Architectural Trade-Off Analysis: Redis vs. Write-Behind Caching (The LSM-Tree Analogy)

An LSM-tree storage engine (like Cassandra or RocksDB) operates similarly to a write-behind cache: updates are written immediately to a fast in-memory structure (MemTable) and sequentially appended to a Write-Ahead Log (WAL) before being asynchronously flushed down to permanent disk storage (SSTables) in the background.

Redis operates with the same lightning write speed but flips the primary dataset ownership: the RAM structure is the source of truth, not a buffer.

| Architectural Vector | Redis Cache / Database | LSM-Tree Database (Cassandra/RocksDB) |
|---|---|---|
| Primary Data Home | RAM only. If data exceeds system memory limits, Redis crashes or evicts data. | Disk pages. RAM is merely an entry buffer for fast sequential ingest. |
| Durability Control | Optional snapshots (RDB) or log appends (AOF) written asynchronously to disk. | Strict durability; updates are committed to an active disk WAL before write confirmation. |
| Primary Advantage | Deterministic sub-millisecond response latencies across all data structures. | Ability to handle petabyte-scale write workloads that far exceed RAM capacity constraints. |

---

## 7. Persistence & Durability: RDB vs. AOF

Redis is in-memory first, but a process crash or restart would lose everything without a durability mechanism. Two independent, combinable options exist:

| Mechanism | How It Works | Durability | Recovery Speed | Cost |
|---|---|---|---|---|
| **RDB (snapshotting)** | Forks the process and writes a full point-in-time binary dump of the dataset to disk at configured intervals (e.g., "every 60s if 1000+ keys changed"). | Weak — can lose up to the whole interval's worth of writes on crash. | Fast (loading one compact binary file). | Low CPU/disk overhead; the `fork()` briefly doubles memory (copy-on-write). |
| **AOF (append-only file)** | Logs every write command to a file, replayed sequentially on restart. `appendfsync` controls flush frequency: `always` (fsync every write, slowest, safest), `everysec` (default, ≤1s of loss), `no` (OS decides, fastest, least safe). | Strong with `everysec`/`always`. | Slower (replaying a command log); mitigated by periodic AOF rewrite/compaction. | Higher disk I/O and larger file size than RDB. |

**Production default:** run both — RDB for fast full backups/restores, AOF (`everysec`) for tighter durability — and let Redis reconcile them on restart (AOF takes precedence if both are present, since it's more current). Pure caching use cases where the source of truth is another database often disable persistence entirely, since a cold cache just repopulates from misses.

---

## 8. High Availability: Replication & Sentinel

* **Primary-Replica Replication:** A primary asynchronously streams its write stream to one or more replicas. Replicas serve reads (scaling read throughput) but reject direct writes. Replication is asynchronous by default, so a replica can lag — a failover can lose the last few unreplicated writes.
* **Redis Sentinel:** A separate set of Sentinel processes (run 3+, quorum-based, same odd-number-for-majority reasoning as any consensus system) monitors primary/replica health via heartbeats. On primary failure, Sentinels vote and promote the most up-to-date replica to primary, then reconfigure the rest to follow it and inform clients of the new address.
* **Failover cost:** Sentinel failover is not instant — there's a detection window (missed heartbeats) plus promotion time, during which writes fail. This is the same "minority side can't make progress safely" trade-off seen in Raft, applied to cache/primary availability rather than a data path.

---

## 9. Redis Cluster (Native Horizontal Scaling)

Redis also ships a native clustering mode as an alternative to the client-side consistent hashing in §5 — the more common answer when an interviewer asks "how does Redis itself shard, without an external proxy?"

* **Hash Slots, Not a Continuous Ring:** The keyspace is divided into a fixed **16,384 hash slots**. Each key is mapped to a slot via `CRC16(key) mod 16384`, and each slot is owned by exactly one master node. This is simpler to reason about and rebalance than a continuous hash ring — resharding means moving whole slots between nodes, not recomputing arbitrary ring positions.
* **Hash Tags for Multi-Key Operations:** Redis Cluster doesn't support multi-key commands (`MGET`, transactions) across slots by default, since that would require cross-node coordination. Using a **hash tag** — `{user1000}.profile` and `{user1000}.sessions` — forces both keys onto the same slot (only the substring inside `{}` is hashed), enabling atomic multi-key operations on logically related data.
* **Per-Slot Replication:** Each master slot owner has its own replicas; on a master's failure, Cluster's internal gossip protocol detects it and promotes a replica for just that slot range — failure is localized to the affected slots, not the whole cluster.
* **Client Awareness Required:** Cluster-aware clients cache the slot-to-node mapping and get redirected (`MOVED`/`ASK` responses) when they hit a node that doesn't currently own the requested slot (e.g., mid-resharding).

---

## 10. Memory Management: Eviction Policies

Since RAM is finite, `maxmemory` plus a `maxmemory-policy` decide what happens once the limit is hit — a frequent interview probe ("what happens when your cache is full?"):

* `noeviction` — reject new writes with an error once full; reads still work. Dangerous default for a pure cache (breaks the app instead of shedding data).
* `allkeys-lru` / `allkeys-lfu` — evict the least-recently-used / least-frequently-used key across the entire keyspace. The standard choice for a general-purpose cache.
* `volatile-lru` / `volatile-lfu` / `volatile-ttl` — only consider keys that have a TTL set, evicting by recency/frequency/soonest-to-expire. Useful when some keys (e.g., persistent config) must never be evicted regardless of memory pressure.
* `allkeys-random` / `volatile-random` — evict a random candidate; cheaper CPU cost, rarely the right trade-off vs. LRU/LFU unless access patterns are already uniform.

**LRU is approximate, not exact:** Redis samples a small random set of keys (`maxmemory-samples`, default 5) and evicts the oldest among the sample rather than tracking a perfect global LRU list, trading a small accuracy loss for O(1)-ish eviction cost instead of maintaining an expensive exact ordering structure.

---

## 11. Messaging: Pub/Sub vs. Streams

Both let Redis act as a message broker, but they solve different problems — a common interview trap is treating them as interchangeable:

| Feature | Pub/Sub | Streams (`XADD`/`XREAD`) |
|---|---|---|
| Delivery guarantee | Fire-and-forget. A message published with no subscribers connected is lost forever. | Persisted, append-only log. Consumers can replay from any offset. |
| Consumer model | Every subscriber gets every message (broadcast). | Consumer Groups allow work to be load-balanced across a pool, each message delivered to exactly one consumer in the group. |
| Use case fit | Real-time fan-out where losing a message during a disconnect is acceptable (e.g., live typing indicators, ephemeral notifications). | Durable event/task processing where at-least-once delivery and replay matter (e.g., activity feeds, event sourcing, task queues with acknowledgment). |

If an interview scenario needs "don't lose the message if the consumer was briefly down," that's a signal to reach for Streams (or an external broker like Kafka/SQS), not Pub/Sub.

---

## 12. Probabilistic Data Structures

For scenarios where an approximate answer at a fraction of the memory cost is an acceptable trade-off:

* **HyperLogLog (`PFADD`/`PFCOUNT`):** Estimates the cardinality (unique count) of a huge set using a fixed ~12KB of memory regardless of whether you're counting thousands or billions of elements, with ~0.81% standard error. Classic use: "count unique daily visitors" without storing every visitor ID.
* **Bitmaps (`SETBIT`/`BITCOUNT`):** A string treated as a raw bit array. Extremely memory-dense for boolean flags at scale — e.g., a 1-bit-per-user "did user X log in today" tracker across 100M users costs ~12.5MB.
* **Bloom Filter (via RedisBloom module):** Answers "is this element *definitely not* in the set, or *possibly* in it?" with no false negatives but a tunable false-positive rate, in a fraction of the memory a real set would need. Classic use: check-before-hitting-the-database gate (e.g., "has this username been taken?") to avoid a wasted disk lookup on definite misses.

---

## 13. Common Interview Pitfalls & Patterns

* **Cache Stampede / Thundering Herd:** A hot key expires and hundreds of concurrent requests all miss simultaneously, all hammering the origin database at once to repopulate it. Mitigations: a short-lived "recompute lock" (only one request rebuilds the cache, others wait or serve stale), jittered TTLs so keys don't expire in lockstep, or serving stale-while-revalidate.
* **Hot Key Problem:** A single key (e.g., a viral post) receives disproportionate traffic, overwhelming the one shard/node that owns it — sharding by key doesn't help since it's still one key. Mitigation: replicate the hot key's value across multiple keys/nodes (`post:123:copy1..N`) and have clients pick one at random, or promote it to local in-process caching on the app servers themselves.
* **Big Key Problem:** A single key backing an enormous value (a list/hash/set with millions of members) makes any O(N) operation on it (even `DEL`) block the single-threaded event loop, and complicates resharding since a key can't be split across cluster slots. Mitigation: shard the logical entity across multiple smaller keys (e.g., bucket a huge set by hash prefix) instead of one giant one.
* **Cache Invalidation Strategy Choice:**
  * *Cache-aside (lazy loading):* App checks cache → miss → reads DB → writes result to cache. Simple, only caches what's actually requested, but every miss pays full DB latency.
  * *Write-through:* App writes to cache and DB together (synchronously). Cache is never stale, but write latency includes both.
  * *Write-behind (write-back):* App writes to cache immediately, DB write is deferred/batched asynchronously. Fastest writes, but risks data loss if Redis crashes before the flush.
* **Rate Limiting with Redis:** Two common patterns interviewers expect:
  * *Fixed counter:* `INCR rate:{user}:{minute}` + `EXPIRE` on first increment — simple, O(1), but allows a burst at window boundaries (double the limit across two adjacent windows).
  * *Sliding window log:* a ZSET per user with request timestamps as scores; `ZREMRANGEBYSCORE` to drop entries older than the window, `ZCARD` to count what remains. More accurate, more memory/CPU per check.
