# System Design Study Notes: Remote Procedure Calls (RPC)

## 1. RPC Fundamentals

Remote Procedure Call (RPC) lets a client invoke a function on a remote server as if it were a local function call. Instead of thinking in terms of HTTP verbs and URLs (as with REST), the caller thinks in terms of a function signature, e.g. `userService.GetUser(42)` — the network plumbing is hidden behind normal-looking code.

### The Request Lifecycle

1. **Client stub:** The caller invokes a local "stub" function, e.g. `client.GetUser(ctx, &GetUserRequest{Id: 42})`.
2. **Marshalling (serialization):** The stub packages the function name and arguments into bytes (JSON, Protobuf, Thrift binary, etc.).
3. **Transport:** Bytes travel over the network (TCP, HTTP/2, etc.) to the server.
4. **Server skeleton:** The server unpacks the request, resolves which function was called, and invokes the real implementation.
5. **Response:** The return value is serialized and sent back, then unmarshalled into a native object on the client, which receives it as an ordinary return value.

This client-stub/server-skeleton pairing is normally generated automatically from an **Interface Definition Language (IDL)**. The service contract is defined once, and a compiler generates client and server code in whatever languages are needed.

---

## 2. RPC vs REST: Architectural Comparison

| Dimension | REST | RPC (e.g., gRPC) |
|---|---|---|
| Mental Model | Resources + verbs (`GET /users/42`). | Actions/functions (`GetUser(42)`). |
| Payload Format | Usually JSON — text-based, human-readable. | Usually binary (Protobuf/Thrift) — smaller and faster to parse. |
| Contract | Loose. Often documented separately (OpenAPI is optional). | Strict, enforced by an IDL (`.proto` file). Client and server cannot drift silently. |
| Transport | Typically HTTP/1.1. | Typically HTTP/2 (gRPC) — multiplexed streams, header compression. |
| Streaming | Awkward. Requires bolted-on solutions (SSE, WebSockets). | Native — client-streaming, server-streaming, and bidirectional streaming. |
| Browser Support | Native (`fetch`/XHR). | Needs a translating proxy (grpc-web) — browsers do not speak HTTP/2 trailers well. |
| Best Used For | Public APIs, third-party integrations, simplicity. | Internal microservice-to-microservice calls, low-latency/high-throughput paths. |

---

## 3. Key Concepts

* **IDL (Interface Definition Language):** Protocol Buffers `.proto` files define request/response message shapes and service methods. This schema is the contract both client and server compile against.
* **Serialization Format:** Protobuf/Thrift use binary encoding, which is far smaller and faster to (de)serialize than JSON — at the cost of not being human-readable on the wire.
* **Synchronous vs. Asynchronous RPC:** Classic RPC blocks the caller until a response arrives. Async variants (message-queue-backed RPC, or gRPC's async stubs) let the caller continue without blocking.
* **Streaming Modes (gRPC specifically):**
  * Unary — one request, one response (a normal function call).
  * Server streaming — one request, a stream of responses (e.g., live updates).
  * Client streaming — a stream of requests, one response (e.g., chunked uploads).
  * Bidirectional streaming — both sides stream simultaneously (e.g., chat, live collaboration).
* **Service Discovery:** Because RPC calls a named service rather than a URL, RPC systems are usually paired with a service registry (e.g., Consul) or a service mesh to resolve which host actually handles the call.

---

## 4. Trade-Off Analysis

### Why RPC Wins Internally

* Binary serialization plus HTTP/2 multiplexing yields lower latency and higher throughput than JSON-over-HTTP/1.1.
* Strict typed contracts catch integration bugs at compile time instead of runtime.
* Native streaming avoids hacky long-polling/WebSocket workarounds.

### Why It Is Harder to Use at the Edge

* Binary payloads are not debuggable with `curl` and a text editor the way JSON is.
* Browsers cannot natively speak gRPC — a translating proxy (Envoy, grpc-web) is required.
* Tight coupling to a schema requires real backward-compatibility discipline (in Protobuf: never renumber or reuse field tags, only add new optional fields).

### Failure Semantics: The Classic RPC Gotcha

Because RPC *looks* like a local call, it is easy to forget that the network can fail mid-call. If a client times out, it genuinely does not know whether the server executed the action or not (partial failure). This is why idempotency keys and retry policies with backoff are a standard RPC design topic — a non-idempotent RPC (e.g., "charge card") should never be blindly retried without a deduplication mechanism.

---

## 5. Common RPC Frameworks

* **gRPC** (Google) — HTTP/2 + Protobuf. The modern default for microservices.
* **Thrift** (Apache/Facebook) — similar model, predates gRPC, multi-language.
* **JSON-RPC / XML-RPC** — simple, human-readable, HTTP/1.1-based, less common today.
* **CORBA / Java RMI** — older technologies, mostly historical/legacy context.

---

## 6. Worked Example: gRPC in Go

This example defines a `UserService` with a single `GetUser` unary RPC, then implements both the server and the client in Go.

### 6.1 The Contract (`user.proto`)

```protobuf
syntax = "proto3";

package user;

option go_package = "example.com/rpcdemo/userpb";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
}

message GetUserRequest {
  int32 id = 1;
}

message GetUserResponse {
  int32 id = 1;
  string name = 2;
  string role = 3;
}
```

Generate the Go stubs with:

```bash
protoc --go_out=. --go-grpc_out=. user.proto
```

This produces `userpb.pb.go` (message types) and `userpb_grpc.pb.go` (client stub + server interface) — the code you would otherwise hand-write for marshalling and transport.

### 6.2 The Server

```go
package main

import (
	"context"
	"log"
	"net"

	"google.golang.org/grpc"
	pb "example.com/rpcdemo/userpb"
)

// server implements the generated UserServiceServer interface.
type server struct {
	pb.UnimplementedUserServiceServer
}

func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
	// In a real service this would hit a database.
	return &pb.GetUserResponse{
		Id:   req.Id,
		Name: "Alex Xu",
		Role: "admin",
	}, nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterUserServiceServer(grpcServer, &server{})

	log.Println("gRPC server listening on :50051")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
```

### 6.3 The Client

```go
package main

import (
	"context"
	"log"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	pb "example.com/rpcdemo/userpb"
)

func main() {
	conn, err := grpc.NewClient("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("failed to connect: %v", err)
	}
	defer conn.Close()

	client := pb.NewUserServiceClient(conn)

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	resp, err := client.GetUser(ctx, &pb.GetUserRequest{Id: 42})
	if err != nil {
		log.Fatalf("GetUser failed: %v", err)
	}

	log.Printf("User %d: name=%s role=%s", resp.Id, resp.Name, resp.Role)
}
```

### 6.4 What This Demonstrates

* The client calls `client.GetUser(ctx, ...)` — a plain Go method call. The generated stub handles marshalling the request into Protobuf, sending it over an HTTP/2 connection, and unmarshalling the response.
* `context.WithTimeout` is idiomatic Go for bounding an RPC's lifetime — this is exactly how a client protects itself from the partial-failure problem described in Section 4: if the deadline expires, the call returns an error rather than hanging indefinitely.
* The service contract (`user.proto`) is the single source of truth. Changing the response shape means regenerating stubs for every consuming service, which is what gives gRPC its compile-time safety compared to REST's implicit contracts.
* Swapping `GetUser` for a `stream GetUserResponse` return type in the `.proto` file, with no other architectural changes, is how you would move to server-streaming — the transport and codegen already support it.
