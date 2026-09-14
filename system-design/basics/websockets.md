# WebSockets — System Design Notes

> Companion to `server_sent_event.md`. SSE = server→client only, plain HTTP, browser auto-reconnects, works great when *any* server node can serve *any* client because the payload is identical for everyone (broadcast). WebSocket (RFC 6455) = persistent, full-duplex, bidirectional over a single TCP connection, needed when the client must also push data back with low latency, or when a message has to reach one *specific* connected user rather than "whoever's subscribed."
>
> Template: (1) Explain, (2) Problem solved, (3) Mechanism, (4) Go mechanics, (5) Delta vs. SSE/polling, (6) The real scaling problem, (7) Failure modes, (8) Scale intuition, (9) Architecture placement, (10) Interview trigger.

---

## 1. Explain

A WebSocket starts as a normal HTTP request that asks to be upgraded, then the same TCP connection is repurposed to carry a lightweight framed protocol in both directions for as long as it stays open. No repeated HTTP overhead (headers, TCP/TLS setup) per message after that — once upgraded, per-frame wrapping overhead drops to roughly **2–10 bytes**, vs. the full HTTP header block SSE/polling re-pays (implicitly, once per stream) or a REST call pays every single request.

## 2. Problem solved

Plain HTTP is strictly request→response, client-initiated. Polling (repeatedly asking "anything new?") and even SSE (server keeps pushing, but only one direction) can't cover the case where the client also needs to send low-latency updates — cursor position, a typed message, a game input — without opening a new request each time. WebSocket gives one connection, both directions, minimal per-message overhead.

## 3. Mechanism — the handshake and after

- **Handshake:** client sends a normal-looking HTTP GET (on port 80/443, `ws://` or `wss://` scheme) with `Upgrade: websocket`, `Connection: Upgrade`, `Sec-WebSocket-Key`, and `Sec-WebSocket-Version: 13`. Server replies `101 Switching Protocols` with `Sec-WebSocket-Accept` (a hash of the key, proving it understood the request) — this is the one and only HTTP exchange.
- **After that:** the HTTP layer is peeled away entirely. The same TCP socket now carries WebSocket **frames**, not HTTP messages — an opcode (text, binary, ping, pong, close) plus payload. Client→server frames are masked (an anti-cache-poisoning-proxy requirement), server→client frames aren't.
- **Keep-alive:** ping/pong control frames detect a dead connection (no TCP-level signal tells you a peer vanished without closing cleanly — NAT/proxy timeouts and mobile radio drops are silent). Missed pongs past a threshold = treat as dead, clean up.
- **Transport:** plain TCP (`ws://`) or TLS-wrapped (`wss://`) — same relationship as `http://`/`https://`.

```
  Client                                    Server
    │   GET /chat HTTP/1.1                    │
    │   Upgrade: websocket                    │
    │   Connection: Upgrade                   │
    │   Sec-WebSocket-Key: dGhlIHNhbXBsZQ==    │
    │   Sec-WebSocket-Version: 13               │
    ├──────────────────────────────────────────►│
    │                                           │
    │   HTTP/1.1 101 Switching Protocols        │
    │   Upgrade: websocket                      │
    │   Sec-WebSocket-Accept: s3pPLMBi...       │
    │◄──────────────────────────────────────────┤
    │                                           │
    │======= same TCP connection, now WS framing =======
    │                                           │
    │  ── text/binary frame (either direction) ──►
    │  ◄── text/binary frame (either direction) ──
    │  ──────────────────────────────── ping ────►
    │  ◄──────────────────────────────── pong ────
```

Only the first exchange is HTTP. Everything after the `101` is framed WebSocket traffic on the same socket — that's the entire point: one connection setup, then cheap bidirectional messages for as long as it stays open.

## 4. Go mechanics — upgrade, the full-duplex loop, and the concurrent-write trap

Real servers don't hand-roll frame parsing — `gorilla/websocket` is the standard Go library. It hijacks the underlying HTTP connection object and hands you a persistent `conn` to read from and write to directly:

```go
package main

import (
	"fmt"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true }, // CORS policy
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	// Hijack the HTTP connection and upgrade it to a persistent socket
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Println("Upgrade failed:", err)
		return
	}
	defer conn.Close()

	for {
		// Blocks waiting for the next incoming frame from this client
		messageType, payload, err := conn.ReadMessage()
		if err != nil {
			fmt.Println("Read failed (client likely disconnected):", err)
			break
		}
		// Naive echo — fine for a demo, NOT fine once anything else also writes to conn (see below)
		conn.WriteMessage(messageType, []byte("Server Echo: "+string(payload)))
	}
}
```

**The trap:** a `gorilla/websocket` connection is **not safe for concurrent writes**. The read loop above runs on one goroutine, but real servers also need a *second* source of writes — e.g. the presence/backplane subscriber in §6 pushing a message that arrived from another server. If that background goroutine calls `conn.WriteMessage()` at the same moment the read-loop's echo does, you get a race condition and a panic, not a queued write.

**The fix — a per-connection outbound channel:** never let more than one goroutine touch `.WriteMessage` directly. Give each session its own `chan []byte`; any code that wants to send to that user pushes onto the channel; a single dedicated writer goroutine per connection drains it and is the *only* caller of `.WriteMessage`. Read loop and write loop become two independent goroutines per connection, coordinated only through that channel — never sharing the write call itself.

## 5. Delta vs. SSE / long polling

The full protocol-comparison table is already in `server_sent_event.md` — don't re-derive it, just the piece that table doesn't capture:

- **SSE's stock-ticker case study (already in your notes) is a broadcast pattern:** any server node can serve any subscriber because "AAPL is $230" is the same payload for every viewer. No per-user routing needed — that's *why* the O(1)-firehose-into-local-registry design in that note works so cleanly.
- **WebSocket's hard case is point-to-point:** a chat message or a personal notification must reach *one specific* user's open socket, and that socket lives on exactly *one* specific server instance. This — not "which protocol" — is what interviewers are actually probing when they ask you to design a chat app. (SSE has the identical problem for per-user pushes — see `server_sent_event.md` §5, added as a companion to this section.)

## 6. The real scaling problem: connection affinity + the routing backplane

This is the section worth over-preparing, since it's the deep-dive interviewers steer toward:

- A WebSocket connection is **stateful and pinned** to whichever server instance accepted its handshake — unlike stateless HTTP, you can't load-balance individual messages across the pool. The connection itself only needs to survive at one node; the problem is everyone *else* reaching it.
- **Consequence:** when some other backend service (or another user) wants to push to user X, it has no way to know which of your N gateway instances is holding X's socket — unless something tracks that.
- **Standard fix — a presence/routing layer:** a shared store (Redis, or a dedicated presence service) maps `userID → gateway instance ID`. To deliver to user X: look up the mapping, publish the message on a channel/topic scoped to that specific instance, and only that instance forwards it down the one open socket it actually holds.
- **Simpler (but less efficient) alternative — broadcast-to-all-and-filter-locally:** every instance subscribes to one global channel (`PUBLISH user_messages '{"target":"UserB","body":"hello"}'`); every instance receives every message and checks its own local connection registry, discarding anything it doesn't hold. No presence store to keep consistent — but every message does O(N) work across N instances instead of O(1) targeted delivery, so it stops scaling once message volume or instance count grows. Worth naming both and explicitly picking the presence-store version for the "how does this scale to hundreds of thousands of users" follow-up — the broadcast version is the simpler thing to mention first, then upgrade from.
- **Same firehose idea as the SSE note, inverted:** SSE's Kafka-backed fanout is "one event → broadcast to whichever local users on this server happen to care" (nobody needs to know *which* server a viewer is on). WebSocket point-to-point routing is "one event for exactly one user → find the *single* server holding them → deliver only there." Same building blocks (pub/sub backplane, local registry map), opposite fan-out shape.
- Presence entries need a **TTL/heartbeat**, not just an on-disconnect cleanup hook — a server that crashes ungracefully never fires its cleanup, and a stale mapping means messages get routed into the void.

```
  [Notification Service]       [Chat Service]
          │                          │   both directions now possible:
          │ "push to U55"            │   U55 can also SEND a message up
          ▼                          ▼
  ┌────────────────────────────────────┐
  │ Presence Store (Redis): U55 → GW-2    │
  └────────────────────────────────────┘
          │
          │ publish on GW-2's scoped channel
          ▼
  ┌────────────────────────────────────┐
  │ Pub/Sub Backplane (Redis / Kafka)     │
  └────────────────────────────────────┘
          │
    ┌─────┴──────┐
    ▼             ▼
 ┌──────┐     ┌──────┐
 │ GW-1  │     │ GW-2  │ ◄── holds U55's live socket
 └──────┘     └───┬──┘
                    │   ▲
   server → client  │   │  client → server
   (pushed from      ▼   │  (U55 typing/sending —
    backend)      [ U55's device ]   the arrow SSE doesn't have)
```

The only structural difference from the SSE point-to-point diagram (`server_sent_event.md` §5) is that bottom arrow going *up* — the client can originate traffic too, which is the entire reason to pick WebSocket over SSE once a use case needs it.

## 7. Failure modes

- **Idle-timeout kill:** standard reverse proxies (NGINX, AWS ALB, Cloudflare) are built for HTTP traffic and default to tearing down a connection after **~60 seconds** of silence to save resources — mitigate by running an internal ticker that sends a **ping every ~30 seconds** (well under the 60s cutoff), which the client answers with pong automatically; this artificial heartbeat is what keeps proxies from ever seeing "idle" traffic in the first place.
- **Reconnect storm:** a server restart/deploy drops every connection on that instance at once → all those clients reconnect simultaneously → thundering herd on whichever instances survive. Mitigate with jittered exponential backoff, never immediate retry.
- **Message loss across a reconnect:** WebSocket has no built-in equivalent of SSE's `Last-Event-ID`. You build it yourself — sequence numbers per message, client reports its last-seen sequence on reconnect, server replays the gap from a durable log (or accepts the gap for best-effort use cases like live cursors).
- **Stale presence entries:** covered above — TTL/heartbeat, not just graceful-close cleanup.
- **Concurrent-write panics:** covered in §4 — a connection object shared across goroutines without a single-writer channel pattern will eventually race and crash, not just misbehave.

## 8. Scale intuition

- Each open connection costs a file descriptor + a buffer (tens of KB, roughly) — event-loop/async servers (Node, Go, Netty) comfortably hold 10K–100K+ concurrent connections per instance with OS tuning; thread-per-connection servers exhaust RAM in the low thousands (this is literally "Bottleneck B" already named in your SSE note — identical constraint, same fix: async I/O).
- System-wide concurrent-connection ceiling = (connections per gateway instance) × (number of gateway instances) — that's the number to say out loud when asked "how many users can this hold online at once," not a vague "it scales horizontally."

## 9. Architecture placement

- Sits behind a WebSocket-aware L7 LB/proxy that passes the `Upgrade` header through (modern ALB/NGINX/Envoy do; not a given on older infra).
- Usually its own **connection-gateway tier**, separate from business-logic services — its only job is holding sockets and talking to the presence/routing backplane, which keeps it scalable independently of whatever's behind it.

## 10. Interview trigger

"Design a chat app / live notifications / multiplayer game / collaborative editor (Figma)" — naming WebSocket as the transport is table stakes. The actual signal is whether you volunteer the **connection-affinity + presence/routing-backplane** problem unprompted, the same way your replication notes flag volunteering PACELC as the Staff-level signal on CAP questions. A second, sharper signal: naming the concurrent-write trap (§4) unprompted when asked how the server pushes an async event down to a client that's also mid-read — that's an implementation-depth detail most candidates miss entirely.

---

## Quick self-test
1. Why can't you round-robin WebSocket messages across a stateless server pool the way you would plain HTTP requests?
2. What's the structural difference between the SSE stock-ticker fanout (already in your notes) and WebSocket point-to-point delivery to one user?
3. Name two independent reasons a "successfully connected" WebSocket can still lose messages.
4. What's the one extra arrow in the WebSocket backplane diagram that the SSE point-to-point diagram doesn't have — and why does it exist?
5. Why does a WebSocket connection panic under concurrent writes, and what's the one-sentence fix?
6. What's the trade-off between the presence-store approach and the broadcast-to-all-and-filter-locally approach for routing a message to one user?

## Open threads / to revisit
- Next natural pairing: rate limiting (token bucket vs leaky bucket) or caching — both flagged as remaining building-block gaps in the 10-day sprint plan.
- Worth revisiting once you've done a chat-app mock: does your presence-layer answer hold up against "what if Redis (the presence store) itself goes down" follow-up?


🎯 Architectural Summary:

State Affinity Boundary: WebSockets are structurally Stateful. Connection affinity is pinned into the local memory of a single host. Horizontal routing demands a cross-cluster Pub/Sub Broker Mesh Layer to coordinate message delivery between decoupled servers.

Concurrency Memory Demarcation: Relational WebSocket libraries do not support thread-safe writes. To secure the runtime against racing conditions and panics, you must deploy an Asynchronous Single-Writer Abstraction. Client structs use internal channels acting as mailboxes, ensuring only one specific goroutine interacts with the network socket hardware buffer.

Intermediate Keep-Alives: Reverse proxies aggressively reap idle TCP streams. To maintain connection integrity, you configure application-level Ping/Pong Heartbeat Control Frames to transition low-overhead packets over the pipe periodically, verifying structural network liveness without generating application database overhead.Would you like to compile this multi-server WebSocket mesh architecture into your study notes, or transition to a different enterprise architectural trade-off analysis, like WebSockets vs gRPC Streaming?