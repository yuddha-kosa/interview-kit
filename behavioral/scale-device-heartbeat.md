Absolutely. For your notes, I’d capture this as a **production scaling/design discussion**, including both what you actually did and the deeper design reasoning we discussed.

# Device Heartbeat Scaling — Detailed Design Discussion

## 1. Problem

We had thousands of edge devices sending periodic heartbeat messages to the platform.

A heartbeat contained:

* Device heartbeat/status information
* Current device details
* Metrics such as CPU, memory, temperature, network information, etc.

The original flow was:

```text
Device
   ↓
Gateway
   ↓
Message Queue
   ↓
Heartbeat Consumer
   ↓
Relational Database
```

The relational database stored information such as:

```text
device_id
last_seen
device_status
device_details
...
```

Device health was derived from heartbeat activity.

For example:

```text
Heartbeat received
       ↓
last_seen = now
       ↓
Device considered healthy

No heartbeat for N minutes
       ↓
Device considered unhealthy/inactive
```

As the number of devices increased, heartbeat processing started consuming a large number of database connections and generating a very high volume of database writes.

This affected unrelated services because the heartbeat workload could consume most of the database connection pool.

---

# 2. First Mitigation

The immediate production problem was **database connection exhaustion**.

So the first protection was to make sure the heartbeat service could not consume all available database connections.

Conceptually:

```text
                  PostgreSQL
                      │
          ┌───────────┴───────────┐
          │                       │
   Heartbeat Service        Other Services
          │                       │
     bounded pool            protected pool
```

This isolated the heartbeat workload from other services.

However, this only protected the database from connection exhaustion.

It did not solve the fundamental problem:

> We were using a relational database as a high-frequency current-state store.

---

# 3. Identifying the Real Problem

The key insight was:

> **Heartbeat frequency and device state-change frequency are very different.**

Suppose:

```text
10,000 devices
2 heartbeats/minute/device
```

That produces:

```text
10,000 × 2 = 20,000 heartbeat writes/minute
```

But the majority of those heartbeats do not represent a meaningful state change.

For example:

```text
10:00  Device A → heartbeat → ACTIVE
10:00:30 Device A → heartbeat → ACTIVE
10:01  Device A → heartbeat → ACTIVE
10:01:30 Device A → heartbeat → ACTIVE
...
```

The relational database does not necessarily need a write for every one of those events.

The meaningful changes are more like:

```text
ACTIVE → INACTIVE
INACTIVE → ACTIVE
```

Therefore, we needed to separate:

### High-frequency ephemeral state

* Latest heartbeat
* Current device status
* Last-seen information
* Short-lived state

from:

### Durable/queryable state

* Meaningful device state transitions
* Data that other services need to query
* Historical metrics

---

# 4. Redis as the Current-State Layer

We introduced Redis as the high-frequency state store.

New architecture:

```text
Device
   ↓
Gateway
   ↓
Message Queue
   ↓
Heartbeat Consumer
   ↓
Redis
```

Redis holds the latest/current heartbeat state for a device.

For example:

```text
device:A
{
    status: ACTIVE,
    last_heartbeat: 10:01:30,
    ...
}
```

Instead of every heartbeat producing a PostgreSQL write, the heartbeat primarily updates Redis.

Redis is a much better fit for this access pattern because:

* Very high write throughput
* Low latency
* Current-state access
* TTL support
* The data is naturally ephemeral/current-state data

PostgreSQL remains the durable relational/queryable store.

---

# 5. TTL-Based Device Health

A heartbeat refreshes the device's TTL in Redis.

For example:

```text
Heartbeat interval: ~30 seconds
Health timeout: several minutes
```

Every heartbeat:

```text
Device A heartbeat
       ↓
Redis SET/UPDATE
       ↓
Refresh TTL
```

If the device stops sending heartbeats:

```text
No heartbeat
     ↓
TTL expires
     ↓
Device is considered stale/inactive
```

Redis expiration is not treated as an exact real-time clock.

There can be some delay between the nominal TTL expiration and processing the resulting event.

That is acceptable because the health requirement is **eventually consistent**.

For example, if the device is supposed to be marked unhealthy after approximately 10 minutes, being a few seconds late is acceptable.

---

# 6. Do Not Write PostgreSQL Directly From Redis Expiration

An important design decision is that Redis expiration does not directly perform a synchronous PostgreSQL update.

Instead:

```text
Redis TTL expiration
        ↓
State-change event
        ↓
Queue
        ↓
DB worker
        ↓
PostgreSQL
```

The queue provides:

* Durability
* Decoupling
* Retry
* Backpressure
* Protection for PostgreSQL

This means PostgreSQL does not have to absorb a sudden burst of state-change events.

---

# 7. Only Persist Meaningful State Changes

Consider a device that remains healthy:

```text
ACTIVE
  ↓
heartbeat
  ↓
ACTIVE
  ↓
heartbeat
  ↓
ACTIVE
  ↓
heartbeat
  ↓
ACTIVE
```

There is no reason to continuously update PostgreSQL.

Instead, PostgreSQL is updated when the logical state changes:

```text
ACTIVE
   ↓
(no heartbeats)
   ↓
INACTIVE
```

and later:

```text
INACTIVE
   ↓
heartbeat received
   ↓
ACTIVE
```

This dramatically reduces database write volume.

The database becomes a durable representation of meaningful device state rather than a sink for every heartbeat.

---

# 8. Handling Bursts / Thundering Herd

A significant failure scenario is a large number of devices becoming inactive simultaneously.

For example:

```text
Factory shuts down
       ↓
10,000 devices stop sending heartbeats
       ↓
Many Redis TTLs expire
       ↓
Large number of state-change events
```

If every expiration immediately resulted in a database update, PostgreSQL could again become overloaded.

Therefore, the queue acts as a buffer:

```text
Redis
  ↓
10,000 expiration events
  ↓
Queue
  ↓
Bounded number of DB workers
  ↓
PostgreSQL
```

The DB workers use bounded concurrency.

For example, instead of allowing thousands of simultaneous updates:

```text
Queue: 10,000 messages

Workers process:
     ↓
bounded concurrency

Remaining messages:
     ↓
stay in queue
```

This provides downstream backpressure.

The key principle is:

> **Absorb bursts upstream and control the rate at which PostgreSQL receives work.**

---

# 9. Database Failure During State Update

Suppose the state-change worker receives:

```text
Device A → INACTIVE
```

but PostgreSQL is unavailable.

We should not lose the event.

Instead:

```text
State-change Queue
       ↓
DB Worker
       ↓
PostgreSQL failure
       ↓
Retry
```

Retries should use:

* Exponential backoff
* Jitter
* Bounded retry attempts

Avoid immediately retrying thousands of failed messages because that can create a retry storm.

After retry exhaustion:

```text
Retry exhausted
       ↓
DLQ
       ↓
Investigation / recovery
```

---

# 10. Redis Failure

Redis is now an important part of the heartbeat path, so Redis failure needs explicit handling.

The durable queue remains the safety net.

Conceptually:

```text
Device
  ↓
Queue
  ↓
Consumer
  ↓
Redis
```

If Redis becomes unavailable:

```text
Consumer
   ↓
Redis failure
   ↓
Circuit breaker opens
```

The consumer should stop continuously pulling work and immediately failing against Redis.

The queue retains the unprocessed messages.

### Circuit breaker states

```text
CLOSED
   ↓
Redis healthy

OPEN
   ↓
Redis unhealthy
   ↓
stop normal processing

HALF-OPEN
   ↓
after cooldown
   ↓
send limited probe

        ┌───────────────┐
        │               │
    Redis healthy    Redis unhealthy
        │               │
        ↓               ↓
     CLOSED            OPEN
```

This prevents a Redis outage from turning into a massive retry storm.

The important principle is:

> **The queue provides durable buffering while Redis is unavailable.**

---

# 11. What About a Redis Outage With a Large Backlog?

Suppose Redis is down for 30 minutes.

During that time, the queue accumulates heartbeat events.

When Redis comes back, the naive approach is:

```text
Replay every heartbeat
       ↓
Redis
```

That is safe but potentially inefficient.

For example:

```text
Device A:
10:00 heartbeat
10:00:30 heartbeat
10:01 heartbeat
10:01:30 heartbeat
...
10:30 heartbeat
```

If only the current state matters, replaying all 60 heartbeats provides little additional value.

We can coalesce current-state events:

```text
Device A
   ↓
many heartbeat events
   ↓
keep latest event
   ↓
one Redis update
```

Conceptually:

```text
Queue backlog
     ↓
Recovery consumer
     ↓
Group by device
     ↓
Select latest heartbeat
     ↓
Redis
```

This reduces unnecessary Redis traffic during recovery.

---

# 12. But Metrics Cannot Be Discarded

The heartbeat payload also contained historical metrics.

For example:

```text
CPU = 70%
Memory = 80%
Temperature = 65°C
Network = ...
```

Those metrics may have historical value and are written to a time-series database.

Therefore, we cannot simply coalesce the entire heartbeat message.

We need to distinguish:

```text
Heartbeat Event
       │
       ├───────────────┐
       │               │
       ↓               ↓
Current State       Historical Metrics
       │               │
       ↓               ↓
Redis             Time-Series DB
```

### Current state

Can potentially be coalesced:

```text
100 heartbeats
     ↓
latest state
     ↓
1 Redis update
```

### Historical metrics

Need to preserve all relevant samples:

```text
100 heartbeat metric samples
     ↓
100 metric samples
     ↓
Time-Series DB
```

This is an important design principle:

> **Different fields in the same event can have different consistency and retention requirements.**

---

# 13. Ordering During Recovery

Once we start coalescing or replaying events, ordering becomes important.

Suppose:

```text
10:00 heartbeat
10:01 heartbeat
10:02 heartbeat
```

The recovery consumer should use the event timestamp, or preferably a device-generated monotonic sequence number if available, to determine which state is newer.

Conceptually:

```text
Device A

Event 1 → timestamp 10:00
Event 2 → timestamp 10:01
Event 3 → timestamp 10:02
```

The 10:02 state should win.

More importantly, an old queued event should not overwrite a newer state that arrived after Redis recovered.

Therefore, Redis state can conceptually contain:

```text
{
    device_id,
    state,
    last_event_timestamp
}
```

When processing a heartbeat:

```text
if incoming_timestamp > stored_timestamp:
        apply update
else:
        ignore stale state
```

A device sequence number can be even stronger than timestamps because device clocks can drift.

---

# 14. TTL During Recovery

There is another subtle issue.

Suppose:

```text
Heartbeat timestamp = 10:00
Redis recovers = 10:20
```

If we process the heartbeat at 10:20 and blindly give it a fresh TTL, we could incorrectly make the device appear healthy for another full heartbeat timeout.

The important distinction is:

```text
Event time
    ≠
Processing time
```

The heartbeat represents what happened at 10:00, not what happened at 10:20.

Therefore, TTL/health calculations should account for the heartbeat's event timestamp.

The exact implementation depends on the system's requirements, but the principle is:

> **Do not let delayed processing make stale events appear fresh.**

The next real heartbeat from the device will refresh the state normally.

---

# 15. Load Shedding / Noisy Devices

Another production concern was a device sending an excessive number of messages.

A single faulty/noisy device should not be able to overload the entire system.

We therefore used load-shedding/rate-control mechanisms.

Conceptually:

```text
Device A → normal traffic
Device B → normal traffic
Device C → huge traffic
```

Instead of allowing Device C to consume all capacity:

```text
Device C
   ↓
Rate limiting / load shedding
   ↓
reduce or reject excessive traffic
```

Where possible, heartbeat intervals can also be adjusted so a noisy device sends heartbeats less frequently.

This provides **fault isolation**.

The principle is:

> **Protect the system from a bad actor/device without penalizing healthy devices.**

---

# 16. Final Architecture

The resulting architecture can be represented as:

```text
                         Edge Devices
                              │
                              │ heartbeat
                              ↓
                         ┌─────────┐
                         │ Gateway │
                         └────┬────┘
                              │
                     rate limiting /
                     load shedding
                              │
                              ↓
                         ┌─────────┐
                         │  Queue  │
                         └────┬────┘
                              │
                     bounded consumers
                              │
                              ↓
                         ┌─────────┐
                         │  Redis  │
                         │ current │
                         │  state  │
                         └────┬────┘
                              │
                         TTL expires
                              │
                              ↓
                    State-change event
                              │
                              ↓
                         ┌─────────┐
                         │  Queue  │
                         └────┬────┘
                              │
                     bounded DB workers
                              │
                              ↓
                       ┌────────────┐
                       │ PostgreSQL │
                       └────────────┘


Heartbeat metrics
       │
       └──────────────────────────────→ Time-Series DB
```

---

# 17. Main Architectural Decisions

### Decision 1 — Protect PostgreSQL

Bound heartbeat-service database connections.

**Reason:**

Prevent heartbeat traffic from starving unrelated services.

---

### Decision 2 — Move high-frequency state to Redis

**Reason:**

Redis is better suited for high-frequency ephemeral/current-state updates.

---

### Decision 3 — Keep PostgreSQL for durable/queryable state

**Reason:**

PostgreSQL remains useful for:

* Durable state
* Queries
* Relationships
* Other services that need relational access

---

### Decision 4 — Persist state transitions rather than every heartbeat

**Reason:**

Heartbeat frequency is much higher than state-change frequency.

---

### Decision 5 — Use queues between components

**Reason:**

Queues provide:

* Durability
* Decoupling
* Backpressure
* Retry
* Burst absorption

---

### Decision 6 — Bound downstream concurrency

**Reason:**

A large burst should not translate directly into thousands of simultaneous PostgreSQL operations.

---

### Decision 7 — Separate current state from historical metrics

**Reason:**

Current state can often be coalesced.

Historical metrics cannot necessarily be discarded.

---

### Decision 8 — Use circuit breakers

**Reason:**

Prevent dependency failures from becoming retry storms.

---

### Decision 9 — Use load shedding

**Reason:**

A noisy device should not be able to consume the capacity of the entire system.

---

# 18. Failure Scenarios

| Failure                                  | Behavior                                                 |
| ---------------------------------------- | -------------------------------------------------------- |
| PostgreSQL connection exhaustion         | Bound heartbeat DB pool                                  |
| PostgreSQL temporarily unavailable       | Queue + retry + backoff                                  |
| DB repeatedly fails                      | DLQ after retry exhaustion                               |
| Redis unavailable                        | Circuit breaker + queue buffering                        |
| Redis recovers                           | Replay backlog; coalesce current-state events where safe |
| Thousands of devices stop simultaneously | Queue absorbs burst + bounded DB workers                 |
| Single device sends excessive traffic    | Rate limiting/load shedding                              |
| Old heartbeat arrives late               | Compare event timestamp/sequence                         |
| Delayed heartbeat replay                 | Don't treat processing time as event time                |
| Historical metrics                       | Replay/preserve independently in time-series DB          |

---

# 19. Key Interview Insight

The strongest way to explain the architectural change is:

> **“The key insight was that heartbeat frequency and state-change frequency were very different. We were using PostgreSQL as a high-frequency current-state store, which created unnecessary write and connection pressure. We moved ephemeral current state to Redis, used TTLs to detect stale devices, and only propagated meaningful state transitions to PostgreSQL. Queues and bounded workers gave us durability, backpressure, and protection against bursts.”**

---

# 20. Staff-Level Lessons

### Separate data according to access pattern

Don't automatically put everything in the relational database.

Ask:

```text
Is this current state?
Is this historical data?
Is it durable?
Is it query-heavy?
Is it ephemeral?
How frequently does it change?
```

The answer determines the appropriate storage system.

---

### Separate event frequency from business-state frequency

A system can receive:

```text
100 events
```

while only having:

```text
1 meaningful state change
```

Persisting every event into the same database may be wasteful.

---

### Protect dependencies

Every downstream dependency should have a capacity boundary:

```text
Gateway → rate limit
Queue → buffer
Consumer → bounded concurrency
Redis → circuit breaker
PostgreSQL → bounded workers
```

A resilient system doesn't assume dependencies are always healthy.

---

### Design for bursts, not just average load

Average traffic may be manageable:

```text
10k heartbeats/min
```

but synchronized events can be much worse:

```text
10k devices stop simultaneously
        ↓
10k state transitions
```

Queues and bounded consumers turn an instantaneous burst into controlled work.

---

### Preserve information according to its value

Not all data deserves the same replay semantics.

```text
Current state → latest value may be sufficient

Historical metrics → individual samples may matter
```

That distinction is what allows recovery to be optimized without accidentally losing important information.
