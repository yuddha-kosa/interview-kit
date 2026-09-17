# System Design Study Notes: Stateless Authentication & Security Architectures (JWT Internals)

## 1. JSON Web Token (JWT) Fundamentals

A JWT (JSON Web Token) is an open standard (RFC 7519) used to securely transmit serialized payload data between systems. The primary architectural benefit is statelessness — the backend relies on cryptographic computation to verify trust instead of querying a centralized session store (e.g., Redis or an SQL database) for every standard request [ZS].

### Structural Blueprint

A JWT string is structured as three distinct cryptographic segments concatenated by dots (`.`): `Header.Payload.Signature`

1. **The Header (Metadata):** Defines the metadata of the token, specifying the token type (JWT) and the hashing algorithm used for the signature (e.g., symmetric HS256 or asymmetric RS256).

   ```json
   {"alg": "HS256", "typ": "JWT"}
   ```

2. **The Payload (The Claims):** Contains assertions/claims about the entity (the user) and custom data properties.

   ```json
   {"sub": "123456", "name": "John Doe", "role": "admin", "exp": 1790000000, "jti": "uuid-v4-token-id"}
   ```

   > **Interview Critical Warning:** Payload data is merely Base64Url encoded, not encrypted. Anyone who intercepts a JWT string can instantly decode it. Sensitive credentials or PII (Personally Identifiable Information) must never be placed inside a standard JWT payload.

3. **The Signature (The Security Shield):** Prevents tampering. It is calculated by taking the encoded header, the encoded payload, a server-side secret key, and feeding them through the designated algorithm.

   ```text
   HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), SERVER_SECRET_KEY)
   ```

---

## 2. Architectural Comparison: Sessions vs. JWTs

| Design Dimension | Traditional Stateful Sessions | Stateless JSON Web Tokens (JWT) |
|---|---|---|
| State Location | Server-Side. Stored in database or RAM cluster (e.g., Redis) [ZS]. | Client-Side. Completely self-contained inside the token string [ZS]. |
| Database Overhead | High. Every incoming API request forces a database/cache read to validate the session ID. | Zero for standard path. Verification relies on CPU cryptographic calculations instead of disk or network I/O. |
| Horizontal Scaling | Complex. Requires sticky sessions at the load balancer or a shared centralized cache tier (Redis). | Excellent. Any independent microservice can handle verification locally if it holds the secret key. |
| Immediate Revocation | Trivial. Deleting the session key from Redis instantly forces a global logout. | Hard. Cryptographically valid until its natural expiration timestamp (`exp`) hits zero. |

---

## 3. Mitigating the In-Flight Token Theft Window

If a user is active online and an attacker intercepts their valid, unexpired access token, the cryptographic signature is mathematically valid. The server cannot natively tell the two users apart. To protect against active token theft, you use a multi-tiered security setup:

### A. Contextual Fingerprinting (Token Binding)

* **The Concept:** Tie the token to the client's physical context. When generating the token, combine the user's IP address and browser profile (User-Agent) into a SHA-256 hash. Embed this hash into a custom claim inside the payload (e.g., `"fp": "9a8b7c..."`).
* **Validation Check:** On every incoming API request, the gateway re-hashes the current connection's IP and User-Agent. If the generated string does not match the embedded `fp` claim, the token is flagged as stolen, blocked, and blacklisted.

### B. Securing Client-Side Storage (Isolating Tokens from XSS)

* Most tokens are stolen via Cross-Site Scripting (XSS) when malicious scripts access local application variables (`localStorage.getItem("token")`).
* **Architectural Fix:** Move the JWT out of local browser storage entirely. Issue the token via an `HttpOnly` Cookie with `Secure` and `SameSite=Strict` flags. When a cookie is marked `HttpOnly`, browser execution engines block JavaScript from reading it, rendering standard XSS data extraction useless.

---

## 4. Advanced Revocation: Dual-Token Architecture

To combine the speed of stateless architecture with immediate access controls, separate your authorization model into two separate lifecycles:

1. **Access Token (The JWT):** Stateless, short lifespan (e.g., 15 minutes). Used for every single microservice endpoint hit.
2. **Refresh Token (Opaque String):** Stateful, long lifespan (e.g., 7 days). Saved securely inside your authentication database/Redis table.

### The Refresh Token Rotation Trap

To catch an attacker who managed to break past device storage and copy both tokens, implement sequential rotation tracking:

* Every single time a client uses a Refresh Token to renew their short-lived Access Token, the server deletes that old Refresh Token and issues a new one, building a sequential token history tree in the database.
* **The Trap Execution:** If an attacker attempts to use an old Refresh Token A that has already been spent by the real user, the server looks at the database logs and instantly recognizes a duplicate token usage event.
* **The Breach Action:** The database trips a fraud alarm. It invalidates the entire session history family branch for that account, immediately revoking all child items and forcing any active client to immediately hard-reauthenticate with credentials.

---

## 5. Production-Scale Invalidation: The Two-Step Pipeline

When a breach is detected via token rotation or a user explicitly clicks "Logout Early," the system must kill the in-flight access token without destroying database performance. You must call out the Layered Verification Pipeline to prove you are not introducing an anti-pattern database read on every request:

```text
[ Incoming Request with JWT ]
             │
             ▼
┌─────────────────────────────────┐
│  Layer 1: Stateless CPU Layer   │ ──► Pure local math. Re-computes signature.
└─────────────────────────────────┘     Drops fake/altered tokens instantly.
             │
             ▼ (If Signature is Valid)
┌─────────────────────────────────┐
│  Layer 2: Stateful Cache Layer  │ ──► Dynamic context validation. Checks Redis or
└─────────────────────────────────┘     Local Gateway Memory for blocklist/version status [ZS].
             │
             ▼ (Passed Both)
[ Forward to Core Microservices ]
```

### Layer 1: The Stateless CPU Layer (Pure Math)

* When a request hits your network edge or API Gateway, it performs local hardware cryptographic verification first. It extracts the headers/payloads, runs the hash math, and verifies the signature matches.
* **DDoS Shielding:** If a malicious bot network floods your cluster with millions of randomized fake tokens, Layer 1 drops 100% of them locally at the CPU level. The system never performs a database or cache lookup for an invalid signature, safeguarding your infrastructure from database exhaustion.

### Layer 2: The Stateful Context Layer (The Lookup)

Only after the token passes the signature check does the server verify its lifecycle status using one of two highly optimized methods:

#### Method A: Session Versioning (Token Salting)

* Instead of signing tokens with a single global static key, include a user-specific version variable in the signing key calculation. Maintain an integer column called `token_version` inside your user database metadata table [ZS].
* Dynamic Key: `Key = SERVER_SECRET_KEY + user.token_version` [ZS]
* **The Invalidation Switch:** When an account is breached or logs out early, execute an atomic write:

  ```sql
  UPDATE users SET token_version = token_version + 1;
  ```

* **The Result:** The very next millisecond, the old token arrives, passes Layer 1 math, but fails verification at Layer 2 because the server is now verifying signatures using the new version integer.

#### Method B: Local Gateway RAM Broadcast (Zero-Network Overhead)

* To avoid hitting a centralized database, your authentication system can maintain a Blocklist instead of an "allow-list".
* **The Mechanism:** When an early logout occurs, the auth node logs the token's unique ID (`jti`) and its remaining lifetime to a distributed Redis cache. Simultaneously, it broadcasts this event via a Pub/Sub queue (like Kafka or Redis Pub/Sub) to all active API Gateway instances.
* **In-Memory Lookups:** Each API Gateway registers this `jti` into its own local hardware RAM (a high-speed HashSet or Bloom Filter). Layer 2 lookups remain highly local and efficient.
* **Self-Cleaning Memory:** Because the access token lifecycle is short (15 minutes), the API Gateway only holds that blocked ID in RAM for its remaining lifespan. Once the 15-minute mark passes, the token naturally expires on its own, and the Gateway safely evicts the ID from RAM to prevent memory leaks.
