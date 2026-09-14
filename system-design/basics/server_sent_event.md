## 📌 System Design Study Notes: Real-Time Streaming Architectures (Server-Sent Events)

> Companion to `websockets.md`. SSE = server→client only, plain HTTP, browser auto-reconnects — cheapest option when the channel only needs to push, and cleanest when the push is *broadcast* (identical payload to every subscriber). It does **not** avoid the connection-affinity problem for *per-user* pushes — see §5 below, and `websockets.md` §5 for the bidirectional version of the same problem.

------------------------------
## 🏗️ 1. Server-Sent Events (SSE) Fundamentals
Server-Sent Events (SSE) is a server push technology enabling browsers to receive automatic, real-time streaming data from an HTTP server over a single, long-lived connection. It serves as a modern alternative to traditional short/long polling.

## 📊 Protocol Comparison

| Feature | Long Polling | Server-Sent Events (SSE) | WebSockets |
|---|---|---|---|
| Communication Direction | Unidirectional (Client-driven cycle). | Unidirectional (Server streams infinitely to client). | Bidirectional (Full-duplex; both sides stream simultaneously). |
| Protocol Foundation | Standard HTTP | Standard HTTP / HTTP/2 | Custom framed protocol over TCP, reached via an HTTP Upgrade (`ws://` / `wss://`). |
| Network Overhead | High. Constant reconnects & header serialization. | Low. Single persistent HTTP stream connection. | Low. Single persistent connection after protocol upgrade. |
| Firewall Friendly | Yes. Standard HTTP ports (80/443). | Yes. Leverages native HTTP routing paths. | Mostly fine today on modern LBs/proxies (ALB, NGINX, Envoy pass `Upgrade` through) — was more of a real problem on older/locked-down corporate proxies, worth naming as a legacy caveat rather than a current blocker. |
| Data Format | Any (JSON, Text, Binary) | Strictly UTF-8 Plain-Text | Text or Binary (Bytes, Buffers). |
| Primary Use Cases | Legacy system fallback. | Real-time feeds, financial tickers, dashboards, LLM text streaming (ChatGPT). | Chat applications, multi-player gaming, collaborative editing (Figma). |

------------------------------
## ⚡ 2. Under the Hood: The Streaming Interface
SSE looks exactly like a standard REST API endpoint, but it alters underlying HTTP contract headers to prevent the network socket from closing.

## The Underlying Network Exchange

* The Request: Client requests a streaming stream:

GET /api/v1/stream HTTP/1.1
Accept: text/event-stream
Connection: keep-alive

* The Response Header: Server signals it will stream data fragments continuously:

HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

* The Data Wire Format: Information must be plain-text chunks separated strictly by double newlines (\n\n). Events can be assigned optional names (event:) and unique sequence trackers (id:):

event: progress
id: 1042
data: {"step": 1, "status": "processing"}

------------------------------
## 🚧 3. Scalability Roadblocks & Mitigations

## 🚧 Bottleneck A: The Max Connection Limit (HTTP/1.1)

* The Flaw: Under HTTP/1.1, browsers enforce a strict limit of 6 persistent connections per domain. Opening more than 6 tabs across your application freezes the browser network layer.
* The Fix: Force HTTP/2 or HTTP/3 configuration at the Load Balancer level. HTTP/2 utilizes Multiplexing, letting hundreds of distinct SSE data streams share one single TCP pipe.

## 🚧 Bottleneck B: Server Thread Exhaustion

* The Flaw: Multi-threaded web frameworks (like traditional Apache or Tomcat) tie one full OS thread to each active connection. Streaming to 10,000 users triggers 10,000 threads, exhausting server RAM instantly.
* The Fix: Deploy an Asynchronous Event-Driven I/O Engine (Go, Node.js, or Netty). These park idle connections in an event loop, using virtually zero system overhead when no data is actively flowing.

## 🚧 Bottleneck C: Disconnection Data Loss

* The Flaw: If a mobile client crosses a wireless dead zone, the network drops. During this gap, they miss critical updates streamed by the server.
* The Fix: Leverage the built-in Last-Event-ID protocol. Every time the browser reconnects automatically, it appends the header: Last-Event-ID: 1042. The backend reads this ID, calculates what was missed from an event store, and replays missing fragments seamlessly.

------------------------------
## 🚀 4. High-Scale Architecture: Real-time Stock Ticker (Case Study) — the BROADCAST pattern
Imagine designing a live stock ticker for a 10-stock watchlist scaled across hundreds of thousands of concurrent users split among multiple backend nodes.

## ❌ The Core Design Anti-Patterns

* Do not create a channel per stock: Generating 10 channels for 10 stocks on every single user connection causes memory allocation spikes.
* Do not poll a central cache inside user threads: Spawning thousands of goroutines running for { readCache() } loops creates severe Lock Contention and wasted CPU cycles.
* Do not bind broker subscriptions dynamically: Registering a network subscription to your message broker (like Redis or Kafka) only when a user joins creates an O(U) connection pool bottleneck that crashes your system.

## The Production-Grade Event-Sourcing Blueprint
To build a resilient platform, deploy a Static Firehose Consumer Architecture integrated with a Local Parallel Chunk Worker Pool. This works cleanly because every subscriber to "AAPL" wants the *identical* payload — no server needs to know *which specific user* it's serving, only *whether it has any watchers at all*. That assumption is what breaks in §5 below.

### Cluster-level view

```
                    Clients (many, GET /stream, Accept: text/event-stream)
                                        │
                                        ▼
                          ┌───────────────────────┐
                          │     Load Balancer       │   no sticky routing needed —
                          └───────────────────────┘   any instance can serve any client
                               │              │
                               ▼              ▼
                    ┌────────────────┐  ┌────────────────┐
                    │  SSE Server A   │  │  SSE Server B   │   (async I/O, not
                    └────────────────┘  └────────────────┘    thread-per-connection)
                               ▲              ▲
                               │              │
                    ┌─────────────────────────────────┐
                    │   Kafka: ticker.*  (live feed)    │ ◄── External Stock Exchange
                    └─────────────────────────────────┘
```

### Inside each SSE server instance (symmetric, independent of every other instance)

```
   Kafka consumer — one fixed subscription per instance, O(1), never grows with user count
             │
             ▼
   Local Registry Map:  "AAPL" → []ClientSession   (who on THIS instance watches AAPL)
             │   (price update for AAPL arrives → look up local watchers only)
             ▼
   Chunk the watcher list into batches (e.g. 2,000 users per chunk)
             │
             ▼
   Buffered Task Channel  ──►  Worker Pool (parallel goroutines, one per CPU core)
                                        │
                         non-blocking write; a slow/backed-up client is
                         dropped for this tick rather than stalling the batch
                                        ▼
                              client.Stream ──► flusher.Flush()
                                        │
                                        ▼
                                [ Browser / EventSource ]
```

## Step 1: Static O(1) Broker Firehose
When an individual SSE Server Node boots up, it establishes exactly one single, permanent connection to the central message broker (e.g., using a Kafka consumer group or a Redis PSUBSCRIBE ticker:*). The network subscription footprint is fixed at O(1) and never increases when users connect.

## Step 2: Single-Channel Multiplexing
Every unique connection instantiates one single data channel per user, not one per stock. This channel handles a rich StockUpdate struct containing both the symbol name and price. The user's connection thread blocks cleanly inside a select statement, consuming 0% CPU while waiting.

## Step 3: Local Memory Registry Maps
The server maintains a thread-safe registry mapping a stock symbol to a slice of local active user pointers: map[string][]*ClientSession. When an event for AAPL arrives over the server's single broker firehose, it extracts its local client slice. If no local clients are watching it, the server discards the packet instantly.

## Step 4: The Internal Task Queue & Parallel Chunking Pool
To completely eliminate inner-loop propagation delays (head-of-line blocking where User 10,000 experiences lag compared to User 1):

   1. The main ingestion worker breaks large target client lists into manageable chunks (e.g., blocks of 2,000 users).
   2. It packages these chunks into a discrete data structure (FanOutTask) and posts them to an internal, buffered Go Task Channel (chan FanOutTask).
   3. A pool of dedicated Parallel Fan-Out Goroutines continuously reads from this channel, dividing the workload concurrently across all hardware CPU cores.

## Step 5: Non-Blocking Writes via http.Flusher
When workers write to user channels, they use a non-blocking select layout with a default fallback case. If a specific user's network is lagging and their buffer fills up, the worker skips them instantly to prevent stalling the entire loop queue. Valid connections call flusher.Flush() to bypass internal server buffers and force the packet down the wire immediately.

------------------------------
## 🎯 5. The Other Case: Per-User SSE Delivery (POINT-TO-POINT) — the gap broadcast doesn't cover

The stock-ticker design above works *because* the payload is identical for every subscriber, so no server needs to know which specific user it's talking to. A real notification ("your order shipped", "Alice liked your comment") has to reach exactly **one** user, and that user's SSE connection is still pinned to exactly **one** server instance — SSE does not remove this problem, it only doesn't come up in a broadcast example. This is the same connection-affinity problem `websockets.md` §5 covers for chat — the fix is identical: a presence/routing layer.

```
  [Order Service]  (business logic — holds no client connections itself)
         │
         │ 1. "notify user U1042: order shipped"
         ▼
  ┌───────────────────────────────┐
  │ Presence Store (Redis)          │   userID → owning instance
  │  U1042 → SSE-Server-B            │   (written by Server B on connect,
  └───────────────────────────────┘    refreshed via TTL/heartbeat)
         │
         │ 2. publish on the channel scoped to SSE-Server-B
         ▼
  ┌───────────────────────────────┐
  │ Pub/Sub Backplane                │  (Redis Pub/Sub / Kafka)
  └───────────────────────────────┘
         │
         │ 3. only SSE-Server-B is subscribed to this channel
   ┌─────┴──────┐
   ▼             ▼
┌────────┐   ┌────────┐
│Server A │   │Server B │ ◄── holds U1042's actual open connection
└────────┘   └────┬───┘
                    │ 4. write directly to U1042's open stream
                    ▼
            [ User 1042's browser ]
```

If the presence entry is missing or stale (instance crashed without a clean close, TTL expired), the notification has nowhere to go — this is exactly why the entry needs a heartbeat-refreshed TTL, not just an on-disconnect cleanup hook.

------------------------------
## 🛑 6. When NOT to Use SSE

- **Client needs to push data proactively, not just occasionally.** SSE is one-way by construction — a typed chat message or a collaborative-cursor position needs WebSocket.
- **Binary payloads.** SSE is strictly UTF-8 text; base64-encoding binary data over it defeats the efficiency you were reaching for. Use WebSocket.
- **You'll likely need the reverse channel soon anyway.** If today's "just push notifications" feature is realistically going to grow a "client sends something back" requirement, WebSocket buys you that for free later — SSE doesn't.
- **You cannot guarantee HTTP/2 in front of it and expect real multi-tab usage.** Without HTTP/2 multiplexing, the 6-connections-per-domain cap (Bottleneck A) bites fast.

------------------------------
## 🎯 7. Interview Trigger

"Design a live feed / notification system / real-time dashboard / LLM token streaming" → SSE is the expected default whenever the channel is server→client only. The signal that separates a senior answer from a staff one: explicitly naming whether the use case is **broadcast** (stock ticker — no presence layer needed, any instance serves any client) or **point-to-point** (order notification — presence layer required), rather than just saying "I'll use SSE" and stopping there.

------------------------------
## 📄 8. Core Go Code Layout for Notes

```go
// The task structure placed into our parallel worker loop queue
type FanOutTask struct {
    Update  StockUpdate
    Targets []*ClientSession
}

// Ingestion pipeline that divides user workloads into concurrent tasks
func ProcessIncomingMarketUpdate(update StockUpdate) {
    Registry.mu.RLock()
    allWatchers := Registry.Watchers[update.Symbol]
    // Quick memory copy under read lock to maintain concurrency safety
    watchersCopy := make([]*ClientSession, len(allWatchers))
    copy(watchersCopy, allWatchers)
    Registry.mu.RUnlock()

    const chunkSize = 2000
    for i := 0; i < len(watchersCopy); i += chunkSize {
        end := i + chunkSize
        if end > len(watchersCopy) {
            end = len(watchersCopy)
        }

        // Submit chunk assignment to multi-threaded worker pool queue
        TaskQueue <- FanOutTask{
            Update:  update,
            Targets: watchersCopy[i:end],
        }
    }
}

// Parallel Worker Routine running across multiple CPU cores
func StartFanOutWorker() {
    for task := range TaskQueue {
        for _, client := range task.Targets {
            select {
            case client.Stream <- task.Update: // Instant non-blocking push
            default: // Drop slow clients instantly to preserve system throughput
            }
        }
    }
}
```

------------------------------
## Open threads / to revisit
- Rate limiting (token bucket vs. leaky bucket) and caching are the next building-block gaps — same ones flagged in the 10-day sprint plan and in `websockets.md`.
- Stress-test §5's presence design against "what if Redis itself goes down" — open question shared with `websockets.md`.
