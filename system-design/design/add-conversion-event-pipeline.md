Absolutely. Below is a consolidated set of notes for the **Whop Conversion-Event Pipeline** design, including the architecture, reasoning, failure modes, replay, attribution, schema evolution, reconciliation, and the important interview nuances we discussed.

# Whop Ads — Conversion Event Pipeline

## 1. Problem Statement

Design a system that reliably delivers conversion events from Whop to advertising platforms such as:

* Meta
* TikTok
* Google

Example:

```text
Customer purchases a product on Whop
                ↓
        Conversion event
                ↓
       Whop conversion pipeline
        ↙        ↓        ↘
     Meta      TikTok     Google
```

The system should support:

* Near-real-time conversion delivery
* High volume
* Multiple advertising platforms
* Duplicate events
* At-least-once delivery
* External API failures
* Rate limiting
* Retries
* Dead-letter queues
* Replay/backfill
* Historical events
* Attribution
* Schema evolution
* Observability
* Reconciliation
* Data correction
* Platform-specific API differences

---

# 2. Functional Requirements

### Core requirements

1. Receive conversion events when a customer makes a purchase.
2. Deliver the conversion to the appropriate advertising platforms.
3. Support multiple destinations for the same conversion.
4. Avoid duplicate conversions.
5. Retry transient failures.
6. Handle external platform outages.
7. Handle platform rate limits.
8. Support replay/backfill of historical events.
9. Support DLQ replay.
10. Track delivery status.
11. Support attribution of a purchase to a campaign.
12. Detect and investigate discrepancies between Whop and advertising platforms.
13. Support schema evolution without breaking existing consumers.

---

# 3. Non-Functional Requirements

### Reliability

No conversion should be silently lost.

We generally target:

> At-least-once delivery + idempotent processing

rather than claiming exactly-once delivery.

### Availability

The conversion pipeline should continue accepting purchases even if Meta/TikTok/Google is temporarily unavailable.

### Scalability

Example assumption discussed:

```text
10M visitors/day
× 5 events
= 50M events/day
```

Average:

```text
50M / 86,400 ≈ 579 events/sec
```

Design for substantially higher peak traffic, e.g. 10–20× average:

```text
~5K–10K+ events/sec
```

The exact number is an interview assumption rather than a known Whop production number.

### Eventual consistency

Advertising-platform reporting is naturally eventually consistent.

A successful API request does not necessarily mean:

> "Meta has already attributed this conversion."

---

# 4. High-Level Architecture

A strong architecture:

```text
                    ┌────────────────────┐
                    │   Whop Purchase    │
                    │       API          │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Idempotency /      │
                    │ Event Ingestion    │
                    └─────────┬──────────┘
                              │
                              ▼
                         Kafka/Event Bus
                              │
                              ▼
                    ┌────────────────────┐
                    │ Consumer 1         │
                    │ Persist + Enrich   │
                    └─────────┬──────────┘
                              │
                    DB + Outbox / delivery
                              │
                              ▼
                    Delivery Event Stream
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
        Meta Consumer   TikTok Consumer   Google Consumer
              │               │                │
              ▼               ▼                ▼
        Meta Adapter     TikTok Adapter    Google Adapter
              │               │                │
              ▼               ▼                ▼
           Meta API         TikTok API       Google API
```

---

# 5. Why Kafka?

Kafka gives us:

* Durable buffering
* High throughput
* Partition-based parallelism
* Consumer groups
* Independent consumption by destinations
* Replay capability through offsets / republishing
* Decoupling between ingestion and external API delivery

The purchase API should not synchronously wait for Meta/TikTok/Google.

Instead:

```text
Purchase
   ↓
Persist/enqueue
   ↓
Return success
   ↓
Async delivery
```

This prevents an external advertising-platform outage from directly breaking purchases.

---

# 6. Stable Event Identity

A critical concept:

> The business event needs a stable identity.

For example:

```text
purchase_id = P123
```

or:

```text
event_id = E123
```

The same identity should survive retries and replays.

Do NOT generate a new random event ID every time a message is retried.

---

# 7. Client Retry / Duplicate Purchase Requests

Suppose the client sends the same purchase request three times:

```text
Request 1 → P123
Request 2 → P123
Request 3 → P123
```

The ingestion layer should recognize that these represent the same business transaction.

### Do NOT primarily deduplicate using:

```text
user_id
+ product_id
+ campaign_id
+ time window
```

because a user could legitimately buy the same product twice.

Example:

```text
Purchase 1:
U1 + P1 + C1 + $100

Purchase 2:
U1 + P1 + C1 + $100
```

Those are potentially two legitimate purchases.

### Better approach

Use a stable transaction/business identifier:

```text
purchase_id = P123
```

The purchase service should create it once and persist it.

Then:

```text
Request
   ↓
Idempotency check
   ↓
P123 already exists?
    ├── YES → don't create duplicate
    └── NO  → persist P123
```

---

# 8. Canonical Event

A canonical Whop event should contain platform-independent information.

Example initial schema:

```json
{
  "event_id": "E123",
  "user_id": "U123",
  "product_id": "P123",
  "campaign_id": "C123",
  "amount": 100,
  "timestamp": "..."
}
```

Later:

```json
{
  "event_id": "E123",
  "user_id": "U123",
  "product_id": "P123",
  "campaign_id": "C123",
  "amount": 100,
  "timestamp": "...",
  "currency": "USD",
  "country": "US",
  "device": "mobile",
  "click_id": "..."
}
```

The canonical event should not be designed around one advertising platform.

---

# 9. Platform Adapters

Meta, TikTok and Google have different APIs and schemas.

Therefore:

```text
Canonical Whop Event
        │
        ├───────────────┐
        ▼               ▼
   Meta Adapter     TikTok Adapter
        │               │
        ▼               ▼
   Meta format      TikTok format
```

The adapter:

* Maps fields
* Selects fields relevant to the platform
* Handles platform-specific authentication
* Handles platform-specific error semantics
* Handles platform-specific idempotency
* Converts Whop's canonical event into the external API format

The delivery system should own **delivery state**.

The adapter should primarily own **platform communication and translation**.

---

# 10. Consumer Groups

Use separate Kafka consumer groups for each destination.

```text
                         Kafka
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     Meta group       TikTok group      Google group
```

Each group has independent offsets.

Example:

```text
P123 → Meta succeeds
P123 → Google succeeds
P123 → TikTok fails
```

Meta and Google can advance their offsets.

TikTok's consumer group does not commit that event until it is successfully processed or moved into the appropriate retry/DLQ workflow.

Therefore TikTok failure does not block Meta or Google.

---

# 11. Kafka Partitioning

Partitioning should allow parallel processing.

For destination-specific consumers, simply partitioning by:

```text
platform
```

can create a hot partition.

Example:

```text
Meta → partition 0
TikTok → partition 1
Google → partition 2
```

If Meta receives most traffic, Meta becomes the bottleneck.

Instead, use a deterministic shard:

```text
hash(event_id) + platform
```

Conceptually:

```text
Meta-0
Meta-1
Meta-2
...
Meta-N
```

Now Meta delivery can scale horizontally.

---

# 12. Database Design

The canonical event database should be treated as an important source of truth.

We discussed designing around query patterns first.

Typical queries:

### Query 1

```text
campaign_id
+ platform
+ event_type
+ time range
```

### Query 2

```text
platform
+ event_type
+ time range
```

### Query 3

```text
platform
+ time range
```

For Cassandra-like systems, use time-bucketed partitions.

Conceptually:

```text
partition:
campaign + platform + event_type + day

clustering:
event_time
event_id
```

Example:

```text
C123 | Meta | PURCHASE | 2026-10-04
```

For a large time-range query:

```text
Oct 1
Oct 2
Oct 3
Oct 4
...
```

fan out across bounded partitions.

Do not create an unbounded partition containing an entire campaign's history.

---

# 13. Canonical Store vs Query Views

A useful design principle:

> Keep an immutable canonical source of truth and build query-optimized views around it.

The canonical event represents what actually happened.

Additional views can support:

* Campaign queries
* Platform queries
* Delivery queries
* Replay queries
* Operational dashboards

This avoids forcing one physical schema to satisfy every access pattern.

---

# 14. Transactional Outbox

One important failure scenario:

```text
DB write succeeds
Kafka publish fails
```

Without an outbox:

```text
Purchase exists in DB
but no Kafka event
→ conversion may never be delivered
```

Use an outbox:

```text
DB transaction
 ├── Insert canonical event
 └── Insert outbox record
             ↓
        Outbox publisher
             ↓
           Kafka
```

The database transaction guarantees the event and outbox record are committed together.

The publisher can retry Kafka publication.

---

# 15. At-Least-Once Delivery

We should explicitly say:

> The system provides at-least-once delivery.

Messages may be processed more than once.

Example:

```text
Worker
 ↓
send to Meta
 ↓
Meta accepts
 ↓
worker crashes before committing success
 ↓
Kafka message gets processed again
 ↓
send to Meta again
```

Therefore we need idempotency.

---

# 16. Exactly-Once vs Effectively-Once

Avoid saying:

> "We guarantee exactly once."

Across our system and an external API, true exactly-once execution is generally impossible because:

```text
External API call
        +
Local database update
```

cannot be made one atomic transaction.

Instead:

> At-least-once delivery + idempotent processing gives us effectively-once business semantics.

---

# 17. Delivery State

Delivery state belongs in the delivery/orchestration layer.

Example:

```text
conversion_id | destination | status              | attempts | last_error
---------------------------------------------------------------------------
P123          | Meta        | DELIVERED           | 1        | null
P123          | TikTok      | RETRYING            | 3        | 429
P123          | Google      | DELIVERED           | 1        | null
```

Possible states:

```text
PENDING
SENDING
RETRYING
ACCEPTED_BY_PLATFORM
DELIVERED_TO_PLATFORM
FAILED
DLQ
```

Be careful with terminology.

A platform returning HTTP 200 generally means:

> The platform accepted the request.

It does NOT necessarily mean:

> The platform attributed and reported the conversion.

---

# 18. External API Failure

Suppose Meta is unavailable.

The Meta consumer starts seeing:

```text
5xx
timeouts
connection failures
```

Do not continuously hammer Meta.

Use a **circuit breaker**.

```text
CLOSED
   ↓ failures
OPEN
   ↓ cooldown
HALF-OPEN
   ↓ successful probes
CLOSED
```

### Closed

Normal traffic.

### Open

Stop sending requests temporarily.

Events remain durably buffered.

### Half-open

Send a small number of requests.

If successful:

```text
10 → 20 → 40 → 60 → 80 → 100 req/sec
```

gradually ramp up.

If failures return:

```text
HALF-OPEN → OPEN
```

---

# 19. Circuit Breaker vs Rate Limiter vs Backpressure

These are different concepts.

### Circuit breaker

Protects a failing dependency.

> "Meta appears unhealthy; stop hammering it."

### Rate limiter

Controls request rate.

> "Meta allows approximately X requests/sec."

### Backpressure

Controls upstream load when downstream capacity is insufficient.

> "Our delivery backlog is growing; slow down upstream production."

### Retry

Attempts the operation again after a failure.

These mechanisms work together but solve different problems.

---

# 20. Thundering Herd

Suppose Meta is down for 30 minutes.

During that time:

```text
10M events
```

accumulate.

When Meta comes back, releasing everything immediately can create:

```text
10M events
      ↓
huge worker concurrency
      ↓
millions of API calls
      ↓
Meta overloaded
      ↓
429 / 5xx
      ↓
retry storm
```

This is a thundering herd.

Solutions:

* Shared rate limiter
* Worker concurrency limits
* Exponential backoff
* Jitter
* Gradual ramp-up
* Circuit-breaker half-open state

---

# 21. Retry Strategy

Not every error should be retried.

### Transient errors

Examples:

```text
429
500
502
503
504
timeout
network error
```

Usually retry.

### Permanent errors

Examples:

```text
invalid payload
invalid field
authentication/configuration problem
unsupported event
```

Usually don't repeatedly retry forever.

Instead:

```text
bounded retries
      ↓
DLQ
```

---

# 22. Poison Messages

A bad message can otherwise block a Kafka partition.

Example:

```text
P123 → permanently invalid
P124 → valid
P125 → valid
```

If the consumer keeps retrying P123 synchronously:

```text
P123
 ↓ retry
P123
 ↓ retry
P123
...
```

then P124 and P125 may be delayed.

Use asynchronous retry topics / delayed queues:

```text
Main topic
    ↓
Consumer
    ↓ transient failure
Retry topic
    ↓
later retry
```

After bounded retries:

```text
DLQ
```

This prevents one poison message from blocking normal traffic.

---

# 23. DLQ

A DLQ should not simply be a graveyard.

It should have:

* Metrics
* Alerts
* Error classification
* Original event
* Error reason
* Number of attempts
* Destination
* Timestamp
* Correlation/event ID

Example:

```text
event_id = E123
destination = TikTok
attempts = 5
error = invalid_field
```

---

# 24. DLQ Replay

Suppose 100K TikTok events entered the DLQ because of a bug:

```text
wrong field name
```

We fix the adapter.

Then replay the events.

Important:

> Replay the same business event; don't create a new purchase.

Preserve:

```text
event_id = E123
```

Optionally add metadata:

```text
delivery_mode = REPLAY
replay_job_id = R456
```

Then:

```text
DLQ
 ↓
Replay service
 ↓
Replay queue
 ↓
Normal delivery path
 ↓
TikTok adapter
```

This avoids creating a completely separate delivery implementation.

---

# 25. Historical Replay / Backfill

A user may ask:

> "Replay all conversions from last month."

Do not read millions of events and dump them into the real-time queue at once.

Use:

```text
Replay service
     ↓
small time chunks
     ↓
replay queue
     ↓
normal delivery pipeline
```

Example:

```text
10:00–11:00
11:00–12:00
12:00–13:00
...
```

Maintain:

```text
replay_job_id
status
start_time
end_time
progress
last_processed_bucket
```

so replay is resumable.

---

# 26. Real-Time Traffic vs Replay Traffic

Real-time conversion traffic should have higher priority.

Example Meta capacity:

```text
100 req/sec
```

Possible allocation:

```text
Normal traffic: 70
Replay:         30
```

If real-time traffic increases:

```text
Normal: 95
Replay: 5
```

If normal traffic consumes the full capacity:

```text
Normal: 100
Replay: 0
```

Use:

* Shared token bucket
* Weighted fair scheduling
* Priority queues
* Reserved capacity if necessary

A watcher can monitor:

* Real-time queue lag
* Replay queue depth
* API latency
* 429 rate
* Error rate

and throttle/pause replay.

Important terminology:

> Calling this a "replay circuit breaker" is less precise. A circuit breaker generally protects against dependency failure; replay throttling protects real-time capacity.

---

# 27. Attribution

A purchase may need to be associated with a campaign.

Example:

```text
Ad click
   ↓
campaign C123
   ↓
user browses
   ↓
purchase
```

But simply querying:

```text
user_id + product_id
```

may not be enough.

A user can click multiple ads:

```text
Campaign A → click
Campaign B → click
Campaign C → click
Purchase
```

We need an explicit attribution rule.

Example:

> Last-touch attribution within a 7-day window.

---

# 28. Strong Attribution Signals

Prefer strong identity signals.

Possible hierarchy:

```text
1. Platform click ID
   ↓
2. Authenticated user identity
   ↓
3. Trusted first-party identity resolution
   ↓
4. Platform-provided matching
   ↓
5. UNATTRIBUTED
```

Examples of click identifiers include platform-specific click IDs.

Important:

> Event ID is not the same thing as attribution identity.

Two events can have different IDs but belong to the same user/session/click journey.

---

# 29. Don't Invent Attribution

If there is no reliable relationship between a purchase and an ad:

```text
Purchase
 ↓
no reliable campaign relationship
 ↓
UNATTRIBUTED
```

Do not arbitrarily assign it to a campaign just because:

* Same geography
* Same product
* Same user attributes
* Same time
* Same age group

Those can be useful for aggregate analytics or audience optimization, but shouldn't be used to claim individual conversion attribution without a valid signal.

---

# 30. Attribution Service

A possible architecture:

```text
Purchase event
     ↓
Attribution service
     ↓
click history
identity
attribution window
attribution rules
     ↓
Enriched conversion
     ↓
Delivery pipeline
```

Caching can be used for hot attribution data.

But the database/source of truth remains authoritative.

---

# 31. Refund Semantics

Do not mutate the original purchase event.

Example:

```text
E1:
PURCHASE
P123
$100
```

Later:

```text
E2:
REFUND
P123
$100
```

The original event remains immutable.

The adapter translates the refund into whatever correction/reversal semantics the advertising platform supports.

---

# 32. Delivery State vs Business State

Keep these concepts separate.

Example:

```text
Purchase:
P123

Delivery:
Meta → ACCEPTED
TikTok → RETRYING
Google → ACCEPTED
```

A successful Meta API response means:

```text
Meta accepted the request.
```

It doesn't mean:

```text
Meta definitely attributed the conversion.
```

This distinction should be explicitly communicated to merchants.

---

# 33. Observability

Use both **distributed tracing** and **business-level delivery state**.

### Trace

Example:

```text
Purchase API
    ↓
Kafka publish
    ↓
Consumer 1
    ↓
DB transaction
    ↓
Meta delivery
    ↓
Meta API
```

Async boundaries should generally create appropriate child spans/links rather than blindly treating everything as one synchronous span.

Persist correlation information so an event can be followed across asynchronous processing.

### Business state

Tracing is not sufficient for queries such as:

> "Show me all TikTok events stuck in RETRYING for the last 6 hours."

That's what the delivery database/state is for.

---

# 34. Reconciliation

Our internal delivery system can tell us:

```text
"We sent 980 conversions to Meta."
```

But that does not necessarily mean:

```text
"Meta ultimately reported 980 conversions."
```

Therefore periodically compare our data against platform-side reporting/acknowledgment data.

Example:

```text
Campaign       Window          Whop accepted    Meta reported
C123           10–11 UTC         10,000            9,850
C456           10–11 UTC          5,000             4,990
```

This helps identify discrepancies.

Where possible, compare individual conversion IDs:

```text
Whop                 Meta
E123       ───────→   E123
E124       ───────→   E124
E125       ───────→   missing
```

Reconciliation should be grouped by:

* Campaign
* Platform
* Time window
* Event type
* Conversion identifier when available

---

# 35. Reconciliation Does Not Automatically Mean Failure

Suppose:

```text
Whop accepted: 1,000
Meta reported:   950
```

Possible explanations:

* Reporting delay
* Meta deduplication
* Invalid/rejected events
* Attribution rules
* Different attribution windows
* Platform-side matching issues
* Actual Whop delivery bug

Therefore:

> Reconciliation identifies discrepancies; it does not automatically prove our pipeline is broken.

---

# 36. Diagnostic Funnel

When investigating missing conversions, check each stage:

```text
1. Did Whop ingest it?
        ↓
2. Did Consumer 1 persist it?
        ↓
3. Did it enter the delivery queue?
        ↓
4. Did the platform worker process it?
        ↓
5. Did the platform API succeed?
        ↓
6. Did the platform accept/deduplicate/reject it?
        ↓
7. Did the platform attribute/report it?
```

This provides a systematic debugging path.

---

# 37. Schema Evolution

Initial schema:

```json
{
  "event_id": "...",
  "user_id": "...",
  "product_id": "...",
  "campaign_id": "...",
  "amount": 100,
  "timestamp": "..."
}
```

Later:

```json
{
  "event_id": "...",
  "user_id": "...",
  "product_id": "...",
  "campaign_id": "...",
  "amount": 100,
  "timestamp": "...",
  "currency": "USD",
  "country": "US",
  "device": "mobile",
  "click_id": "..."
}
```

Use versioning:

```text
schema_version = 1
schema_version = 2
```

New fields should preferably be additive and optional.

---

# 38. Backward-Compatible Consumers

A V2 consumer should ideally understand V1 events.

```text
V1 event
   ↓
V2 consumer
   ↓
normalize
   ↓
current internal representation
```

For missing fields:

```text
currency = null
country = null
device = null
click_id = null
```

Don't blindly invent values.

For example:

```text
currency = USD
```

is dangerous if the historical event's currency is actually unknown.

The adapter can decide whether to:

```text
omit field
```

or send it when valid.

---

# 39. Don't Force Every Consumer to Know Platform Schemas

The canonical event should remain platform-independent.

```text
Canonical V2
      ↓
Delivery service
      ↓
Platform adapter
   ├── Meta
   ├── TikTok
   └── Google
```

The adapter decides which fields the destination needs.

This prevents changes to Meta's schema from forcing changes throughout the entire pipeline.

---

# 40. Event Schema Version vs Platform API Version

Keep them independent.

Example:

```text
Whop Event V1
      ↓
Canonical representation
      ↓
Meta Adapter → Meta API V3
TikTok Adapter → TikTok API V2
Google Adapter → Google API V4
```

Whop can evolve its event model independently from external API versions.

---

# 41. Old Events and Replay

Suppose V1 events are sitting in Kafka or the database six months later.

Don't assume:

```text
V1 → DLQ
```

just because the current system is V2.

Prefer:

```text
V1
 ↓
schema detection
 ↓
normalization
 ↓
current internal representation
 ↓
current platform adapter
```

If the old event genuinely cannot be safely interpreted:

```text
V1
 ↓
cannot migrate safely
 ↓
DLQ
```

Then investigate and potentially create a migration/transformer before replay.

---

# 42. Data Correction After Attribution Bug

Suppose we discover:

> For the last six hours, 2% of conversions were attributed to the wrong campaign.

First determine blast radius.

Investigate:

* Time window
* Advertiser
* Campaign
* Platform
* Region
* Attribution-service version
* Error rate
* Deployment changes

Example:

```text
10:00–16:00
Meta only
US region
Attribution service v42
Campaigns C1–C50
```

Then identify affected events.

---

# 43. Fix Forward Before Replay

Don't immediately replay millions of events.

First:

```text
Detect problem
     ↓
Identify root cause
     ↓
Hotfix code/config/infra
     ↓
Verify new events are correct
     ↓
Identify historical bad events
     ↓
Correct/replay
```

Otherwise we risk replaying the same bug.

---

# 44. Correcting an Already-Sent Wrong Conversion

Suppose:

```text
Purchase P123

Wrong:
E123 → Campaign A → Meta
```

But it should have been:

```text
Campaign B
```

First choice:

> Use a platform-supported correction/retraction mechanism if available.

Conceptually:

```text
E123 → Campaign A
       ↓
     retract
       ↓
E124 → Campaign B
```

However, don't abuse a real business event such as `REFUND` merely to represent an attribution correction.

A refund means:

> The customer actually received a refund.

It should not mean:

> Our attribution was wrong.

---

# 45. Correction Event and Audit Trail

Maintain the relationship between the original and corrected event.

Example:

```text
purchase_id = P123

E123
campaign = A
status = RETRACTED

E124
campaign = B
correction_of = E123
status = ACCEPTED
```

This preserves auditability.

Important distinction:

```text
purchase_id
```

represents the underlying business conversion.

```text
event_id
```

identifies the event/delivery representation.

Therefore, one purchase can have correction/retraction events without becoming multiple purchases.

---

# 46. Deduplication at Multiple Layers

There are potentially multiple duplicate scenarios.

### Layer 1 — Purchase ingestion

Client retries:

```text
same purchase request
```

Use stable purchase/business ID.

### Layer 2 — Kafka processing

At-least-once consumer processing can happen multiple times.

Use idempotent processing.

### Layer 3 — External API

Crash-after-send-before-recording-success:

```text
Meta accepted
worker crashes
retry
```

Use destination-supported idempotency if available.

If the destination does not support idempotency:

* Use platform-specific reconciliation
* Maintain delivery identity
* Use destination-specific deduplication mechanisms where possible

---

# 47. Why a Local "Already Sent?" Check Is Not Enough

A tempting design is:

```text
DB:
P123 = NOT_SENT

worker:
check DB
call Meta
update DB = SENT
```

But:

```text
DB says NOT_SENT
      ↓
call Meta
      ↓
Meta succeeds
      ↓
worker crashes
      ↓
DB still says NOT_SENT
      ↓
retry
      ↓
Meta receives duplicate
```

Therefore, a local database flag alone cannot provide exactly-once external delivery.

---

# 48. Adapter Responsibilities

The adapter should primarily handle:

* Authentication
* Request construction
* Platform-specific field mapping
* Platform-specific API versions
* Platform-specific error interpretation
* Platform-specific idempotency/reconciliation
* Platform response normalization

Example normalized response:

```json
{
  "accepted": true,
  "platform_event_id": "META123",
  "retryable": false,
  "error_code": null
}
```

The delivery service then updates:

```text
status = ACCEPTED_BY_PLATFORM
```

---

# 49. Why Delivery State Should Not Live Only in the Adapter

If every adapter maintains its own delivery database:

```text
Meta adapter DB
TikTok adapter DB
Google adapter DB
```

operational queries become fragmented.

Instead:

```text
Delivery service
      ↓
canonical delivery state
      ↓
platform adapter
```

This makes it easier to answer:

> "What is the status of P123 across all platforms?"

---

# 50. End-to-End Example

Customer purchases product:

```text
purchase_id = P123
```

### Step 1 — Purchase

```text
Customer
   ↓
Whop Purchase API
```

### Step 2 — Idempotency

```text
P123 doesn't exist
```

Persist it.

### Step 3 — Outbox

Transaction:

```text
purchase event
+
outbox record
```

### Step 4 — Kafka

```text
P123 → Kafka
```

### Step 5 — Consumer 1

Persist/enrich event.

Potential attribution:

```text
campaign_id = C456
```

### Step 6 — Fanout

Separate destination consumers:

```text
Meta
TikTok
Google
```

### Step 7 — Meta

```text
Canonical event
 ↓
Meta adapter
 ↓
Meta API
 ↓
200 Accepted
```

Delivery state:

```text
Meta = ACCEPTED
```

### Step 8 — TikTok

```text
429
```

Delivery state:

```text
TikTok = RETRYING
```

### Step 9 — Retry

After backoff:

```text
TikTok
 ↓
success
```

### Step 10 — Reconciliation

Later:

```text
Whop accepted = 1,000
Meta reported = 995
```

Investigate discrepancy.

---

# 51. Strong Interview Vocabulary

Use these distinctions carefully:

### At-least-once

```text
Message may be delivered more than once.
```

### Idempotency

```text
Processing the same logical event multiple times produces the same business result.
```

### Effectively-once

```text
At-least-once transport + idempotent processing.
```

### Circuit breaker

```text
Protect dependency from repeated failures.
```

### Rate limiter

```text
Control request rate.
```

### Backpressure

```text
Slow upstream producers when downstream capacity is constrained.
```

### Retry

```text
Attempt a transiently failed operation again.
```

### DLQ

```text
Isolate messages that cannot currently be processed normally.
```

### Replay

```text
Reprocess an existing historical event.
```

### Reconciliation

```text
Compare our internal state with an external system's state/reporting.
```

### Attribution

```text
Determine which advertising interaction/campaign should receive credit for a conversion.
```

---

# 52. Strong Staff-Level Design Principles

### Principle 1

**Don't claim exactly-once delivery to external systems.**

Say:

> At-least-once with idempotency.

### Principle 2

**Don't make external platforms part of the purchase critical path.**

Use asynchronous delivery.

### Principle 3

**Don't let one platform's outage block other platforms.**

Use separate consumer groups.

### Principle 4

**Don't let one poison message block an entire partition.**

Use retry topics and DLQs.

### Principle 5

**Don't mix real-time traffic and replay traffic without capacity controls.**

Give real-time traffic priority.

### Principle 6

**Don't use time-window heuristics as the primary duplicate key.**

Use stable business/event identity.

### Principle 7

**Don't confuse delivery with attribution.**

```text
API accepted ≠ conversion attributed
```

### Principle 8

**Don't make the canonical event schema platform-specific.**

Adapters translate to destination-specific schemas.

### Principle 9

**Don't mutate immutable historical business events.**

Create correction/reversal events.

### Principle 10

**Don't rely only on traces.**

Use:

```text
Distributed tracing
+
Business delivery state
+
Metrics
+
Logs
+
Reconciliation
```

---

# 53. Final Architecture

A concise version to draw in an interview:

```text
                         ┌───────────────────┐
                         │   Purchase API    │
                         └─────────┬─────────┘
                                   │
                              Idempotency
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   DB + Outbox     │
                         └─────────┬─────────┘
                                   │
                                   ▼
                              ┌─────────┐
                              │ Kafka   │
                              └────┬────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Consumer /        │
                         │ Attribution       │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         Delivery Event Stream
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
                ▼                  ▼                  ▼
          Meta Consumer      TikTok Consumer    Google Consumer
                │                  │                  │
                ▼                  ▼                  ▼
          Meta Adapter        TikTok Adapter     Google Adapter
                │                  │                  │
                ▼                  ▼                  ▼
             Meta API          TikTok API         Google API

                    ┌─────────────────────────┐
                    │ Delivery State / DB     │
                    └─────────────────────────┘

                    ┌─────────────────────────┐
                    │ Retry Topics / DLQ      │
                    └─────────────────────────┘

                    ┌─────────────────────────┐
                    │ Replay Service          │
                    └─────────────────────────┘

                    ┌─────────────────────────┐
                    │ Reconciliation Service  │
                    └─────────────────────────┘

                    ┌─────────────────────────┐
                    │ Metrics / Traces / Logs │
                    └─────────────────────────┘
```

# 54. 30-Second Interview Summary

If the interviewer asks you to summarize the entire design:

> "I'd make the conversion pipeline asynchronous. The purchase path persists an immutable conversion event with a stable business ID and uses an outbox to reliably publish it to Kafka. From Kafka, I'd use separate consumer groups for Meta, TikTok and Google so each platform can fail independently. Platform-specific adapters translate our canonical event into each platform's schema and handle their API-specific semantics. Delivery would be at-least-once with idempotency rather than claiming exactly-once. I'd use retries with backoff and jitter for transient failures, circuit breakers for unhealthy platforms, rate limiting for platform quotas, and retry topics plus DLQs for poison events. Historical replay would use a separate replay workflow with lower priority than real-time traffic and shared rate limiting. I'd track explicit delivery state separately from distributed traces, because an API acceptance doesn't mean the platform ultimately attributed the conversion. Finally, I'd periodically reconcile our delivery records against platform reporting to detect discrepancies, and I'd use versioned, backward-compatible canonical schemas so old events can continue to be replayed safely."

This is a good design to keep as your **master reference**. For interview prep, I would especially memorize the distinctions in sections **47–52** rather than memorizing the whole architecture verbatim. Those distinctions are where interviewers can tell whether the design is genuinely understood.
