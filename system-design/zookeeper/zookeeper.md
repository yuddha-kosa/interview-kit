Here is a structured, interview-ready cheat sheet summarizing everything we covered today. You can copy and paste this directly into your system design interview study notes.


------------------------------
## 🏗️ Part 2: Distributed Coordination Systems (ZooKeeper Internals)## 1. Ephemeral Nodes & Sessions

* Definition: Temporary data units (znodes) whose life cycle is tied directly to the active client session.
* Core Mechanics: The client establishes a session and sends continuous heartbeats (typically at 1/3 of the session timeout interval). If the client crashes or experiences a network partition, heartbeats stop. Once the Session Timeout clock hits zero, ZooKeeper automatically destroys the ephemeral node.
* Interview Use Cases: Crucial for building Leader Election, Service Discovery (Cluster Membership), and Distributed Locking without risking permanent deadlocks.

## 2. High-Performance Session Tracking (The Expiry Queue)
To achieve high throughput, ZooKeeper completely avoids naive global sweeps or traditional cron jobs to track expired sessions:

* Separation of Concerns: ZooKeeper separates time tracking from data layout using two distinct in-memory structures:
1. ExpiryQueue: Tracks time buckets mapping a Bucket Timestamp -> Set<SessionID>.
   2. DataTree Map: Tracks ownership mapping a SessionID -> Set<Node Paths>.
* Time-Rounding Buckets: Expiration times are rounded up into discrete time intervals governed by tickTime (default 2000ms).
* Constant-Time Heartbeats (O(1)): When a heartbeat arrives, ZooKeeper looks up the session's old bucket using a secondary helper map (SessionID -> Old Bucket Time), removes it, and slides it into a future rounded time bucket. No search loops are required.
* Dedicated Expiry Thread: An internal tracker thread sleeps and wakes up precisely as sequential time buckets mature. It checks only that specific timestamp's bucket. If a SessionID is still inside, it queries the DataTree Map to instantly target and delete its exact node paths.

## 3. Fault Tolerance & Consensus Architecture

* Durability (In-Memory vs. Disk): While data structures are kept in RAM for speed, ZooKeeper guarantees durability by appending all mutations to a Write-Ahead Transaction Log on disk before updating memory or responding to the client. It periodically saves Fuzzy Snapshots as state baselines.
* Leader-Follower (Zab Protocol): ZooKeeper uses a variant of Master-Worker called Leader-Follower.
* The Leader: Processes and sequences all write requests.
   * The Quorum: Writes are broadcasted as proposals to Followers. A transaction is only committed to memory when a strict majority (quorum) of nodes successfully write it to their local disk logs. This prevents split-brain scenarios and ensures instant, automated leader re-elections (under 200ms) if the active Leader crashes.

Would you like to drill down into a specific system design scenario next—such as walking through the precise step-by-step algorithm for how a Leader Election is executed using these nodes, or simulating a network partition (split-brain) case study?

