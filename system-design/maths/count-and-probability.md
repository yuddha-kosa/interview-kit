# 📘 Staff Engineering Interview Reference: Probability & Counting

This comprehensive study note maps advanced counting and probability patterns directly to large-scale system architecture scenarios. Use these structured breakdowns to communicate engineering trade-offs during your senior interviews.

---

## 🧱 Part 1: Counting Fundamentals

### 1. Permutations (nPr) — Order Matters

**Core Formula:** `nPr = n! / (n - r)!`

**System Analogy:** Sequential pipeline execution, primary/secondary ranking, or routing configurations.

**Blueprint Example — Failover Traffic Routing:**

Scenario: You are configuring a high-availability service mesh with a pool of n = 5 distinct data centers (Virginia, Oregon, Dublin, Tokyo, Singapore). The router must assign a primary node, a secondary failover node, and a tertiary fallback node (r = 3).

* **Why order matters:** Selecting [Virginia → Oregon → Dublin] routes 100% of live traffic to Virginia initially. Selecting [Dublin → Oregon → Virginia] routes it to Dublin. Because swapping the positions alters the system's runtime state, it is a permutation.
* **Stepwise math:** For the first slot, you have 5 choices. For the second, 4 remain. For the third, 3 remain.

```
5P3 = 5 × 4 × 3 = 60 unique routing configurations
```

---

### 2. Combinations (nCr) — Order Does NOT Matter

**Core Formula:** `nCr = n! / (r! × (n - r)!)`

**System Analogy:** Consensus clusters, quorum definitions, replication pools, or feature flags where membership is binary.

**Blueprint Example — Distributed DB Consensus Quorums:**

Scenario: You are designing a Raft-based storage engine with n = 5 database nodes. To safely commit a write transaction, the architecture requires a write quorum of r = 3 nodes to acknowledge the operation.

* **Why order doesn't matter:** If Node 1, Node 2, and Node 3 accept the write data, the quorum is satisfied. The cluster state is identical whether Node 1 or Node 3 responded first. Therefore, [Node 1, Node 2, Node 3] is equivalent to [Node 3, Node 2, Node 1].
* **Stepwise math:** Compute the choices step-by-step (5 × 4 × 3 = 60), then divide by the overcount factor (r! = 3 × 2 × 1 = 6) to deduplicate the arrangements:

```
5C3 = 60 / 6 = 10 unique quorums
```

---

### 3. Stars and Bars — Resource Allocation

**Core Formula:** `C(n + k - 1, k - 1)`

**System Analogy:** Thread pool distribution, load balancing, or allocating shared execution resources into distinct application buckets.

**Blueprint Example — Thread Pool Allocation:**

Scenario: An API gateway has a hard ceiling of n = 10 identical executor threads left in a shared pool. You must distribute them across k = 4 distinct application domains (Payments, Inventory, Auth, Analytics). A domain can receive 0 threads if it is idle.

The math: You have 10 identical items (stars) and need 3 dividers (bars) to separate them into 4 distinct bins. This creates 13 total slots (10 + 4 - 1). You choose 3 slots out of 13 to place your bars:

```
C(13, 3) = (13 × 12 × 11) / (3 × 2 × 1) = 286 unique allocation layouts
```

**The "at least one" trap:** If each domain requires at least 1 thread to prevent cold starts, pre-allocate 4 threads immediately. This leaves you with n = 6 remaining threads to distribute freely across the k = 4 domains:

```
C(6 + 4 - 1, 4 - 1) = C(9, 3) = (9 × 8 × 7) / (3 × 2 × 1) = 84 ways
```

---

### 4. The Inclusion-Exclusion Principle — Deduplication

**Core Formula (2 sets):** `|A ∪ B| = |A| + |B| - |A ∩ B|`

**Core Formula (3 sets):** `|A ∪ B ∪ C| = |A| + |B| + |C| - |A ∩ B| - |B ∩ C| - |A ∩ C| + |A ∩ B ∩ C|`

**System Analogy:** Stream processing deduplication, log analysis filters, or multi-tenant database partitioning.

**Blueprint Example — Log Intersection & the LCM Rule:**

Scenario: You are analyzing integers between 1 and 60 to filter traffic events divisible by 2, 3, or 5.

**Why use LCM for intersection (AND):** To find elements that belong to Set A and Set B (`|A ∩ B|`), they must satisfy both rules simultaneously. A number divisible by 2 AND 3 must be a multiple of their least common multiple (LCM), which is 6.

**Calculation, step by step:**

```
1. Individual counts:
   |A| (div by 2) = 60 / 2  = 30
   |B| (div by 3) = 60 / 3  = 20
   |C| (div by 5) = 60 / 5  = 12

2. Pairwise intersections via LCM:
   |A ∩ B| (LCM 6)  = 60 / 6  = 10
   |B ∩ C| (LCM 15) = 60 / 15 = 4
   |A ∩ C| (LCM 10) = 60 / 10 = 6

3. Triple intersection via LCM:
   |A ∩ B ∩ C| (LCM of 2, 3, 5 = 30) = 60 / 30 = 2

Total = (30 + 20 + 12) - (10 + 4 + 6) + 2 = 62 - 20 + 2 = 44 unique events
```

**Interview trap:** If numbers are not prime (e.g., 4 and 6), do not simply multiply them (4 × 6 = 24). Always find the true LCM (LCM(4, 6) = 12) to avoid severe undercounting.

---

## 🎲 Part 2: Probability Fundamentals

### 1. Conditional Probability — Blast Radius Analysis

**Core Formula:** `P(A | B) = P(A ∩ B) / P(B)`

**Blueprint Example — Network Packet Drop Context:**

Scenario: Total network traffic dropped is 2% (`P(Drop) = 0.02`). The probability that a packet is dropped and went through a legacy router is 1.5% (`P(Drop ∩ Legacy) = 0.015`).

Given that a specific packet just dropped, what is the probability it came from the legacy hardware?

```
P(Legacy | Drop) = 0.015 / 0.02 = 0.75  (75% chance)
```

---

### 2. Bayes' Theorem — Signal vs. Noise in System Alerting

**Core Formula:** `P(A | B) = [P(B | A) × P(A)] / P(B)`

**Blueprint Example — Intrusion Detection False Positives:**

Scenario: A security tool has a 99% true positive rate (`P(Alert | Hacker) = 0.99`) and a 1% false positive rate (`P(Alert | User) = 0.01`). Real attacks are highly rare, representing only 0.1% of baseline connections (`P(Hacker) = 0.001`, leaving `P(User) = 0.999`).

**Step 1 — compute total `P(Alert)`:** Find the probability of any alert firing by combining the hacker-alert pool and the normal-user-mistake pool. Out of 100,000 connections:

```
100 are hackers    → tool alerts on 99 of them   (100 × 0.99)
99,900 are users   → tool mistakenly alerts on 999 of them (99,900 × 0.01)
Total alerts on screen = 99 + 999 = 1,098

P(Alert) = (0.99 × 0.001) + (0.01 × 0.999) = 0.01098
```

**Step 2 — invert the conditional probability via Bayes:**

```
P(Hacker | Alert) = [P(Alert | Hacker) × P(Hacker)] / P(Alert)
                   = 0.00099 / 0.01098
                   ≈ 0.0901  (~9%)
```

**Staff engineering takeaway:** Despite the tool being "99% accurate," 91% of your alerts are false alarms because the baseline rate of malicious behavior is extremely tiny.

---

### 3. Independence vs. Mutual Exclusivity — System Isolation

* **Mutual exclusivity** (`P(A ∩ B) = 0`): Events cannot occur simultaneously. In architecture, this maps to explicit state machines (e.g., an HTTP status cannot be both a 200 OK and a 500 Internal Error).
* **Independence** (`P(A ∩ B) = P(A) × P(B)`): The outcome of one event provides zero predictive information about the other. This maps to isolated blast radiuses (e.g., completely separate AWS availability zones with no shared infrastructure dependencies).
* **The core interview rule:** Events can never be both independent and mutually exclusive. If they are mutually exclusive, Event A occurring tells you with 100% certainty that Event B cannot occur — making them heavily dependent.

---

### 4. Linearity of Expectation — The Architectural Shortcut

**Core Formula:** `E[X + Y] = E[X] + E[Y]`

**The superpower:** This theorem holds perfectly true even if X and Y are highly dependent on each other. It allows you to break down highly complex, tangled cascading failures into basic addition.

**Blueprint Example — Microservice Retry Cascades:**

Scenario: A gateway spins up N = 100 parallel microservice requests. They share the same underlying databases and network links; if one service bogs down, it causes cascading load delays across the others (heavy dependency). Telemetry shows a single service averages 2 retries (`E[X_i] = 2`).

To find the expected total retries across the entire system, bypass the complex joint-probability dependencies completely and sum the individual expectations:

```
E[X_total] = E[X_1] + E[X_2] + ... + E[X_100] = 100 × 2 = 200 expected retries
```

---

## 💡 Interview Communication Script

When a problem lands in your interview, use this exact verbal architecture to signal your seniority:

> "To analyze this system's overhead, we could map out the joint probability distribution, but because these components share downstream microservice dependencies, the conditional logic gets highly complex. Instead, I will leverage Linearity of Expectation [or Stars and Bars / Bayes' Theorem]. Because the expected value of a sum scales linearly regardless of internal dependency, we can isolate the operational cost of a single node and project it accurately across our total fleet footprint."
