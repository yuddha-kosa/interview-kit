Absolutely. Below is a **detailed interview-note version** of the three stories we discussed: **Multi-Region HA/DR, Database Selection, and Workflow Orchestration**.

I’ve structured these as notes you can revisit before the Whop interview: **problem → requirements → architecture → decisions → tradeoffs → failure handling → what you should say in an interview → likely follow-ups**.

---

# 1. Multi-Region HA / DR Architecture

## 1.1 The problem

RapidAI's platform processes medical imaging workflows for hospitals.

The high-level flow is:

```text
Hospital / On-Prem
       |
       | DICOM data
       v
   RapidAI Cloud
       |
       v
 AI Processing / Workflows
       |
       v
 Results
       |
       v
 Hospital PACS / downstream systems
```

This is a mission-critical workload because the system is involved in clinical workflows.

The requirements were therefore much stronger than simply "make the service highly available."

### Main requirements

* High availability
* Regional failure handling
* Low latency
* Ability to continue processing during a regional outage
* No loss of source imaging data
* Stateful/chunked uploads
* Durable result storage
* Disaster recovery
* Multi-region deployment
* Ability to support thousands of hospitals
* Controlled operational complexity

The platform had a **99.99% availability target**.

---

# 1.2 Multi-region traffic architecture

The architecture looked roughly like:

```text
                    AWS Global Accelerator
                       /            \
                      /              \
                     v                v
              Region A             Region B
                 |                    |
                ALB                  ALB
                 |                    |
               Kong                 Kong
                 |                    |
             Kubernetes          Kubernetes
                 |                    |
             Orchestra           Orchestra
```

More specifically:

```text
Hospital
   |
   v
AWS Global Accelerator
   |
   +--------------------+
   |                    |
   v                    v
Region A              Region B
   |                    |
  ALB                  ALB
   |                    |
 Kong                  Kong
   |                    |
 K8s Service           K8s Service
   |                    |
Orchestra             Orchestra
```

### Important distinction

**Global Accelerator chooses the region/endpoint.**

**ALB distributes traffic inside the selected region.**

So don't say:

> "ALB decides which region receives traffic."

Instead:

> "Global Accelerator provides the global regional routing/failover layer, while the ALB distributes traffic within the selected region."

---

# 1.3 Why Global Accelerator?

The goal was to provide a stable global entry point while allowing AWS to route traffic toward healthy regional endpoints.

Conceptually:

```text
Hospital
   |
   v
Static/global entry point
   |
   v
Healthy RapidAI region
```

If Region A becomes unavailable:

```text
              Global Accelerator
                 /          \
                X            |
           Region A          |
          unhealthy          v
                        Region B
```

Traffic can move toward Region B.

This avoids requiring hospitals to know individual regional endpoints.

---

# 1.4 Why stickiness mattered

One of the important details in this architecture was **large chunked uploads**.

For example, suppose a ~500 MB file is split into:

```text
Chunk 1
Chunk 2
Chunk 3
...
Chunk 10
```

The system may need all chunks to reach the same processing context.

Conceptually:

```text
Chunk 1 ──┐
Chunk 2 ──┤
Chunk 3 ──┤
Chunk 4 ──┤
           v
       Same pod/context
           |
           v
      Reconstruct file
```

If requests randomly move between pods:

```text
Chunk 1 -> Pod A
Chunk 2 -> Pod B
Chunk 3 -> Pod C
```

then local session state can become a problem.

Therefore, the architecture used affinity/stickiness at the appropriate layers.

You discussed:

* Global Accelerator source-IP/session affinity
* ALB L7 stickiness
* Kubernetes service routing
* Kong/upstream routing

### Important interview correction

Do **not** claim:

> "Headless Service gives us stickiness."

A headless Service primarily exposes pod IPs directly through DNS rather than providing a virtual ClusterIP.

Stickiness has to come from the actual routing/affinity mechanism.

If you don't remember the exact Kong/upstream configuration, say:

> "We exposed the pod endpoints in a way that allowed the gateway/upstream routing layer to maintain the required affinity. The important requirement was that the chunks of a single upload stayed within the same processing context."

That's safer than inventing a specific implementation detail.

---

# 1.5 Health checking

There were multiple layers of health.

You had a custom health mechanism that checked important dependencies/components rather than simply checking whether the process was alive.

For example:

```text
              Health Service
                    |
       +------------+------------+
       |            |            |
       v            v            v
      DB          S3/API       Critical
                              dependencies
       \            |            /
        \           |           /
         +----------+----------+
                    |
              Aggregate health
```

This is important because:

```text
/health = HTTP 200
```

doesn't necessarily mean:

> "This instance can actually process production traffic."

A pod can be alive while:

* DB is unavailable
* S3 is inaccessible
* critical dependency is broken
* required subsystem is unhealthy

Therefore, the health endpoint used for routing/failover needs to represent **meaningful service health**, not merely process liveness.

---

# 1.6 S3 and multi-region durability

The other major part of the HA design was result storage.

There are two concepts you should keep separate:

### S3 MRAP

**Multi-Region Access Point** provides a global access/routing abstraction over multiple S3 buckets.

### Cross-Region Replication

**CRR** actually replicates objects between buckets/regions.

So:

```text
             Application
                  |
                  v
                S3
                  |
          Cross-Region Replication
            /                 \
           v                   v
       Region A              Region B
       Bucket                Bucket
```

MRAP can provide the access abstraction, while CRR provides replication.

### Important interview correction

Don't say:

> "MRAP replicates the objects."

Instead:

> "MRAP provides the multi-region access abstraction; S3 Cross-Region Replication is what provides object replication."

---

# 1.7 What happens during a regional failure?

Suppose:

```text
Region A = unavailable
Region B = healthy
```

The platform can continue processing in Region B.

Results are written to Region B's S3 bucket.

When Region A becomes available again:

```text
Region B S3
    |
    | CRR
    v
Region A S3
```

Objects catch up.

This means the platform doesn't need to synchronously write to both regions before considering the result durable.

That would have increased latency and created availability coupling.

---

# 1.8 Why asynchronous replication?

You effectively chose:

```text
Process
   |
   v
Write locally
   |
   v
Durable S3
   |
   +---- asynchronous replication ---> other region
```

instead of:

```text
Process
   |
   +----> Region A S3
   |
   +----> Region B S3
             |
        wait for both
             |
             v
          success
```

The second design would introduce cross-region latency and failure coupling.

If Region B's S3 is healthy but Region A is unavailable, synchronous dual-write could prevent successful processing.

Asynchronous replication gives you:

* lower write latency
* regional independence
* continued operation during regional failures

The tradeoff is that there is a replication window.

---

# 1.9 On-prem data provides another layer of resilience

One of the strongest points in your architecture is that the source data isn't immediately lost if the cloud processing path fails.

The hospital/on-prem system retains the source data and can retry.

Therefore:

```text
On-Prem
   |
   | upload
   v
Cloud
   |
   X failure
   |
   v
On-Prem still has source
   |
   v
Retry later
```

So avoid saying:

> "We guarantee no data loss."

Better:

> "The source data remains on-prem until successful processing/transfer, so a regional cloud failure doesn't inherently result in loss of the source study."

That's technically much more defensible.

---

# 1.10 Active-active vs downstream limitation

The RapidAI cloud processing layer could operate across multiple regions.

But one important nuance came up during our discussion:

**Not every downstream component was necessarily active-active.**

For example, RMA historically had a single-region/active-passive characteristic.

That creates an interesting situation:

```text
Cloud processing

Region A       Region B
   |              |
   |              |
   +------ S3 ----+
          |
          v
         RMA
```

Suppose processing occurs in Region B:

```text
Region B
   |
   v
S3-B
   |
   | CRR
   v
S3-A
   |
   v
RMA in Region A
```

Eventually the downstream component can consume the replicated result.

### Ownership boundary

This led to one of the strongest architectural concepts from our discussion:

> **S3 is effectively the durable integration boundary between the platform and downstream consumers.**

The platform's responsibility is:

```text
Processing
   |
   v
Durably publish result to S3
```

After that, the downstream system owns:

```text
S3
 |
 v
Queue/consumption
 |
 v
Processing
 |
 v
PACS/downstream
```

This is important in an interview because it shows that you understand **component ownership boundaries**.

---

# 1.11 Recovery and thundering herd

We discussed a potential failure mode:

Suppose Region A was down for a long time and Region B continued processing.

When Region A comes back:

```text
Thousands of objects
        |
        v
Replication catches up
        |
        v
Many downstream events
        |
        v
Potential burst
```

If every replicated object immediately triggers expensive processing, you could create a recovery storm.

A robust downstream architecture would therefore need something like:

```text
S3 event
   |
   v
Durable queue
   |
   v
Bounded workers
   |
   v
Processing
```

with:

* bounded concurrency
* backpressure
* idempotency
* retries
* DLQ
* monitoring

### Important interview wording

Don't say:

> "RMA definitely does this."

unless you know that it does.

Say:

> "That's where I'd put the responsibility on the consuming side. I'd want a durable queue and bounded concurrency so recovery doesn't turn into a thundering herd."

This distinction between **actual architecture** and **what you would design** is very important in an interview.

---

# 1.12 Best interview summary

Your 60-second version:

> "We needed multi-region resilience for a mission-critical imaging platform. We used Global Accelerator as the global routing/failover layer, with ALB, Kong and Kubernetes inside each region. Because uploads were chunked and could be large, we also needed request affinity so a study's chunks stayed within the appropriate processing context.
>
> For durability, we used S3 as the result boundary and replicated objects across regions asynchronously using S3 CRR. That allowed a healthy region to continue processing even when another region was unavailable, without making every write synchronously dependent on both regions.
>
> The source data also remained on-prem, so a cloud-region failure didn't mean losing the original study. Once results were durably published to S3, downstream systems such as RMA owned consumption and recovery. That separation allowed the processing platform to remain active across regions while downstream consumers handled their own backlog and recovery."

---

# 2. Database Selection Story

## 2.1 The problem

You needed to decide what database architecture should support the platform.

The obvious temptation was:

> "We have multi-region requirements, so let's use a distributed SQL database."

You evaluated:

* CockroachDB
* YugabyteDB
* PostgreSQL

But you didn't choose based on marketing/features.

You evaluated them against the **actual workload and deployment constraints**.

---

# 2.2 Requirements

You had several requirements:

### Availability

The system needed HA and regional failure tolerance.

### Latency

Some operations were on the critical data path.

### Compliance

The deployment had healthcare/data-related constraints.

### Deployment flexibility

The same platform needed to work:

* in cloud
* on-prem
* in smaller environments

### Resource constraints

The on-prem deployment couldn't assume a large distributed database cluster.

### Third-party compatibility

This became one of the most important requirements.

You didn't control every application using the database.

---

# 2.3 CockroachDB evaluation

CockroachDB was attractive because it provides distributed SQL with PostgreSQL compatibility.

Conceptually:

```text
Application
    |
Postgres protocol
    |
CockroachDB
    |
+---+---+---+
|   |   |   |
R   R   R
```

It provides:

* replication
* distributed transactions
* automatic range distribution
* Raft
* strong consistency
* failover

But you identified an important issue.

---

# 2.4 PostgreSQL compatibility ≠ behavioral compatibility

CockroachDB supports the PostgreSQL wire protocol and much of the PostgreSQL ecosystem.

But it is not simply:

> "PostgreSQL, but distributed."

One major difference relevant to your workload was **transaction behavior**.

CockroachDB's distributed transaction model can result in transaction retries/serialization failures.

For example:

```text
Transaction A
     |
     v
writes X
     |
     +---- conflict
            |
Transaction B
            |
            v
        retry/abort
```

The application needs to be prepared to retry certain transactions.

That wasn't trivial because some of your third-party components were designed for PostgreSQL semantics and you didn't control their transaction/retry behavior.

This led to one of your strongest interview statements:

> **"PostgreSQL wire compatibility doesn't necessarily mean behavioral compatibility."**

That is a very Staff-level observation.

---

# 2.5 CockroachDB mental model

If asked how CockroachDB works:

```text
                    SQL Gateway
                         |
                         v
              Find relevant ranges
                         |
                         v
                  Leaseholder
                         |
                 +-------+-------+
                 |       |       |
                 v       v       v
              Replica Replica Replica
                 |       |       |
                 +--- Raft quorum ---+
```

Data is divided into ranges.

Each range is replicated.

One replica acts as the **leaseholder** for serving the relevant operations.

Other replicas participate in replication through Raft.

### Important correction

Don't say:

> "Each replica has a lease."

Instead:

> "A range has a leaseholder, while the range is replicated across multiple replicas."

---

# 2.6 YugabyteDB evaluation

YugabyteDB was another attractive option because it provided distributed SQL and PostgreSQL compatibility.

But the version you evaluated had a PostgreSQL/query-layer limitation around the use of **partitioned tables** in the way your workload required.

That was a blocker.

This is another important lesson:

> A theoretically suitable database can still be rejected because of one required workload capability.

You didn't need to argue that YugabyteDB was a bad database.

You needed to say:

> "For our specific workload and version, it didn't satisfy a required query capability."

---

# 2.7 Bombarder — your validation approach

Rather than relying purely on architecture diagrams or vendor documentation, you built a test service called **Bombarder**.

The purpose was to simulate concurrent workloads from different geographic locations.

Conceptually:

```text
             Bombarder
          /      |      \
         v       v       v
      Region A Region B Region C
         \       |       /
          \      |      /
             Database
```

You measured:

* write latency
* read latency
* concurrent operations
* behavior under load
* cross-region behavior

This was an excellent part of the story.

It demonstrates:

> "I don't choose infrastructure based purely on theoretical capability; I validate the actual workload."

---

# 2.8 The resource problem

The distributed databases required a meaningful cluster footprint.

Your evaluation indicated roughly:

```text
3 regions
   |
   +--- ~3 DB nodes/region
   |
   v
~9 nodes
```

and approximately:

```text
~72 CPUs
```

for the deployment profile you were considering.

That might be reasonable for a large cloud-native system.

But your platform also needed to run in smaller/on-prem environments.

Therefore:

```text
Distributed SQL
     |
     +---- Excellent HA
     +---- Excellent scale
     +---- Strong consistency
     |
     X
     |
Too much resource footprint
for smaller deployments
```

This was the decisive architectural insight.

---

# 2.9 Data characteristics changed the decision

You realized that much of the platform's data was not permanent business data.

A lot of it was:

* workflow state
* transient processing data
* operational metadata
* temporary results

with retention around **7–10 days** for much of the workload.

That meant you didn't necessarily need a globally distributed database holding massive amounts of permanent data.

This changed the question from:

> "Which globally distributed database should we use?"

to:

> "How can we isolate workloads so PostgreSQL is sufficient?"

That's a much better architectural question.

---

# 2.10 Final decision: PostgreSQL

You chose PostgreSQL.

But the important point is:

**You didn't simply choose PostgreSQL and hope it would scale.**

You changed the architecture around the database.

The strategy was:

```text
                 Platform
                    |
          +---------+---------+
          |                   |
          v                   v
   Persistent/shared       Transient/
       data                 local data
          |                   |
          v                   v
   Central PostgreSQL      Local PostgreSQL
        / RDS              per deployment
```

You separated workload ownership.

---

# 2.11 Why workload isolation matters

Instead of:

```text
One giant DB
   |
   +-- everything
```

you moved toward:

```text
Persistent platform data
          |
          v
     PostgreSQL/RDS


Local component state
          |
          v
   Local PostgreSQL
```

This prevents one noisy workload from affecting every other workload.

For example:

```text
Third-party component
       |
       v
Local DB
```

rather than:

```text
Third-party component
       |
       v
Shared central DB
       |
       +---- Platform workload
       +---- Other component
       +---- Workflow engine
       +---- etc.
```

This was particularly important because you didn't control all third-party workloads.

---

# 2.12 The architectural principle

This became one of your strongest Staff-level points:

> **"The best database technology isn't necessarily the best architecture."**

Or even better:

> **"Instead of introducing a distributed database to solve every scaling problem, we scaled PostgreSQL by isolating workloads and separating persistent platform data from transient component state."**

This shows that you were optimizing for:

* operational complexity
* resource footprint
* compatibility
* deployment flexibility
* actual workload characteristics

rather than technology novelty.

---

# 2.13 Tradeoff

You gave up some of the automatic distributed-database capabilities.

With PostgreSQL, you need to handle things like:

* failover
* replication
* partitioning
* scaling
* workload isolation
* application-level concurrency

But the benefits were:

* simpler operational model
* strong PostgreSQL ecosystem
* compatibility with existing components
* smaller footprint
* better on-prem viability
* fewer behavioral surprises
* easier debugging

---

# 2.14 Best interview summary

> "We evaluated CockroachDB, YugabyteDB and PostgreSQL against our actual requirements rather than assuming multi-region meant distributed SQL. CockroachDB gave us the HA and distributed consistency model we wanted, but its transaction semantics required applications to handle retryable serialization failures, and some third-party components weren't designed for that. YugabyteDB had a required query-layer limitation around partitioned tables in the version we evaluated.
>
> I also built a workload generator, Bombarder, to test concurrent reads and writes across regions instead of relying only on theoretical benchmarks. We found that a distributed database required roughly a nine-node footprint across three regions and around 72 CPUs for our deployment profile, which was too heavy for our smaller on-prem environments.
>
> We therefore chose PostgreSQL and changed the architecture around it. We separated persistent platform data from transient/local component data and used workload isolation rather than forcing everything into one globally distributed database. The lesson was that the right answer wasn't the most distributed database—it was the simplest architecture that satisfied our actual workload and deployment constraints."

---

# 3. Workflow Orchestration Architecture

This is probably your strongest **architecture evolution** story.

---

# 3.1 The original problem

A study goes through many processing steps.

Conceptually:

```text
Receive study
     |
     v
Validate
     |
     v
Upload
     |
     v
De-identify
     |
     v
Select model
     |
     v
Run AI model
     |
     v
Process result
     |
     v
Deliver result
     |
     v
Complete
```

But there were many more real steps and dependencies.

Some tasks were:

* cheap
* fast
* deterministic

Others were:

* expensive
* GPU-dependent
* long-running
* failure-prone

You didn't want expensive work to execute if a prerequisite had already failed.

---

# 3.2 Why orchestration was necessary

You needed centralized workflow state.

For example:

```text
Task A
 |
 +-- success --> Task B
 |
 +-- failure --> retry
```

And:

```text
Task B
 |
 +-- success --> Task C
 |
 +-- timeout --> retry
 |
 +-- permanent failure --> workflow failure
```

With tens of steps, implementing all of this independently inside every service would become difficult.

Therefore you used **Netflix Conductor** as the workflow engine.

---

# 3.3 The first design

Initially, each AI model had its own complete workflow.

For example:

```text
ICH workflow

Upload
  |
DEID
  |
ICH inference
  |
Result processing
  |
Delivery
```

Then:

```text
LVO workflow

Upload
  |
DEID
  |
LVO inference
  |
Result processing
  |
Delivery
```

Then:

```text
PE workflow

Upload
  |
DEID
  |
PE inference
  |
Result processing
  |
Delivery
```

This looked reasonable initially.

But as the number of models grew:

```text
50+ workflows
```

the same common steps were duplicated everywhere.

---

# 3.4 The maintenance problem

Imagine changing the common upload behavior.

Originally:

```text
50 workflows
   |
   +--- Upload v1
```

Now you need:

```text
Upload v2
```

You potentially have to modify dozens of workflows.

This creates:

* duplicated configuration
* inconsistent behavior
* harder testing
* harder rollout
* higher change risk

You recognized that the workflows contained two fundamentally different types of logic:

### Common orchestration

Things almost every model needed.

### Model-specific logic

Things unique to a particular AI model.

---

# 3.5 The redesigned architecture

You separated those two concerns.

```text
                 Main Workflow
                      |
       +--------------+---------------+
       |              |               |
     Upload          DEID          Delivery
       |              |               |
       +--------------+---------------+
                      |
                Model Selector
                      |
                      v
             Dynamic Sub-Workflow
                      |
        +-------------+-------------+
        |             |             |
      ICH tasks     LVO tasks     PE tasks
```

The architecture therefore became:

```text
Common/Main Workflow
        |
        v
Model Selector
        |
        v
Model-specific Sub-workflow
```

---

# 3.6 Dynamic sub-workflow selection

The incoming study contains the model information.

For example:

```text
model = ICH
```

The selector constructs a workflow name using a convention:

```text
ICH_sub_workflow
```

Then it dynamically invokes that workflow.

For another model:

```text
model = LVO

        ↓

LVO_sub_workflow
```

This gives you a stable main workflow and extensible model workflows.

---

# 3.7 Why this was better

Suppose you add a new model:

```text
New model = PE
```

You create:

```text
PE_sub_workflow
```

and register it with Conductor.

You don't modify the main workflow.

This means:

```text
                    Main workflow
                         |
          +--------------+--------------+
          |              |              |
         ICH            LVO             PE
       workflow       workflow        workflow
```

The main orchestration layer stays stable.

This is one of the best ways to explain the architectural benefit:

> **"We wanted the orchestration core to remain stable while model-specific behavior could evolve independently."**

---

# 3.8 Deployment model

A model deployment includes its corresponding Conductor workflow.

Conceptually:

```text
Model package
     +
Model workflow
     |
     v
Deployment
     |
     v
Workflow registration
     |
     v
Conductor
```

After deployment:

```text
Selector
   |
   | model = ICH
   v
ICH_sub_workflow
```

This avoids modifying the central orchestration workflow every time a model is added.

---

# 3.9 Workflow versioning

Model-specific workflows can change independently.

For example:

```text
ICH workflow v1
```

might be:

```text
Preprocess
   |
Inference
   |
Postprocess
```

while v2 becomes:

```text
Preprocess
   |
Extra validation
   |
Inference
   |
Postprocess
```

The workflow engine's versioning mechanism lets you control which version should execute.

The key principle:

> **Version the workflow when task definitions, inputs, dependencies, or workflow structure changes.**

---

# 3.10 Cloud vs on-prem orchestration

Another strong aspect of the design was that the same orchestration abstraction worked across on-prem and cloud.

The basic workflow begins on-prem.

Conceptually:

```text
On-Prem Workflow
       |
       v
Upload study to cloud
       |
       v
Should processing happen in cloud?
       |
    +--+--+
    |     |
   Yes    No
    |     |
    v     v
Cloud    Local
model    processing
```

If cloud processing is selected:

```text
On-Prem workflow
       |
       v
Wait
       |
       |
       | cloud result
       v
Continue
```

Meanwhile:

```text
Cloud workflow
      |
      v
Model inference
      |
      v
Result
      |
      v
Signal on-prem workflow
```

The on-prem workflow is effectively suspended/waiting for the external result.

Once the result arrives:

```text
Cloud result
     |
     v
Worker signals waiting task
     |
     v
On-prem workflow resumes
```

This is a good example of why a workflow engine was useful.

The process can last minutes or potentially much longer without forcing a synchronous request across the entire system.

---

# 3.11 Task timeout and retry

Each task can have its own timeout/retry behavior.

For example:

```text
Filesystem task
timeout = short
retry = N


AI inference
timeout = much longer
retry = N
```

That's important because not all tasks have the same execution characteristics.

An AI model might legitimately take:

```text
20–30 minutes
```

while a filesystem operation might take:

```text
seconds
```

A single global timeout would therefore be inappropriate.

---

# 3.12 Failure handling

There are multiple failure levels.

### Task failure

```text
Task
 |
 X
 |
retry
```

The workflow engine retries the failed task according to configuration.

---

### Workflow failure

If the broader workflow fails or times out:

```text
Workflow
   |
   X
   |
recovery/replay
```

the broader workflow can be rerun.

But rerunning everything blindly could be expensive.

Suppose:

```text
Upload
  |
DEID
  |
Inference   <-- expensive
  |
Result
```

and inference already succeeded before the workflow crashed.

You don't want to run inference again unnecessarily.

---

# 3.13 Correlation ID

A correlation ID flows through the workflow:

```text
Workflow
   |
   v
Correlation ID
   |
   +---- task A
   |
   +---- task B
   |
   +---- inference
   |
   +---- result
```

If the workflow is replayed, the inference worker can check:

```text
Does result already exist for this correlation ID?
```

If yes:

```text
Result exists
     |
     v
Skip expensive inference
```

If no:

```text
No result
     |
     v
Run inference
```

This is an important distinction:

### Correlation ID

Identifies the same logical request/study across services.

### Idempotency key

A key specifically used to ensure repeated execution has one logical effect.

A correlation ID **can be used as an idempotency key** if the operation actually enforces deduplication, but the two concepts aren't inherently identical.

---

# 3.14 At-least-once execution

One important realization from the discussion was:

You should **not claim exactly-once model execution**.

Suppose:

```text
Inference worker
       |
       v
starts model
       |
       X
worker crashes
```

The workflow engine doesn't necessarily know whether the black-box model:

* never started
* partially executed
* completed
* completed but response was lost

Therefore, retrying can produce:

```text
Execution 1
   |
   X worker crash

Execution 2
   |
   v
same model
```

So the system effectively accepts **at-least-once execution**.

---

# 3.15 Why duplicates can happen

For example:

```text
Workflow timeout
      |
      v
Retry inference
      |
      v
Original inference was actually still running
```

Now:

```text
Inference A
Inference B
```

both may execute.

This is especially possible if model execution is long-running and queueing delays occur.

You discussed an important scenario:

```text
GPU unavailable
      |
      v
Inference waits in queue
      |
      v
Workflow timeout occurs
      |
      v
Workflow retries
      |
      v
Duplicate inference
```

This is a real distributed-systems failure mode.

---

# 3.16 Why deterministic result storage helps

The result is written to a deterministic S3 location based on the logical study/request.

Conceptually:

```text
S3/
  site/
    system/
      model/
        correlation-id
```

So repeated execution can target the same logical location.

Example:

```text
ICH/
  study-123
```

First execution:

```text
write result -> study-123
```

Duplicate execution:

```text
write result -> study-123
```

The deterministic destination prevents arbitrary proliferation of result objects.

This is a form of **idempotent result publication**, even though the underlying inference execution itself may not be exactly-once.

---

# 3.17 Important nuance: model version

We identified one area where you should **not invent an answer**.

If the same correlation ID is processed by:

```text
Model v1
```

and later:

```text
Model v2
```

then correlation ID alone may not be enough to determine whether an existing result is valid for the current model version.

A conceptual future design could include:

```text
logical request ID
+
model ID
+
model version
```

but you weren't certain how the current production implementation handles that.

If asked in an interview:

> "How do you handle model version changes?"

don't pretend.

Say:

> "The correlation ID handles replay of the same logical request, but I'd want to verify the current production behavior around model-version changes before claiming that correlation ID alone is sufficient. Conceptually, model version should be part of the result identity or validation."

That is a much stronger answer than making something up.

---

# 3.18 What happens if model deployment fails?

The deployment also registers the workflow.

Conceptually:

```text
Deploy model
    |
    +--> deploy model artifacts
    |
    +--> register workflow
```

If workflow registration fails:

```text
Selector
   |
   v
Expected sub-workflow
   |
   X not found/available
   |
   v
Workflow/task failure
```

The study doesn't disappear.

The source data remains on the on-prem system and the failure becomes visible through the failed-workflow/processing mechanism.

After fixing the deployment:

```text
Failed study
     |
     v
Replay
     |
     v
Workflow
```

This is another important resilience property.

---

# 3.19 Capacity and queueing

There was another subtle failure mode.

Suppose the AI model needs GPU:

```text
Study
 |
 v
Queue
 |
 | GPU unavailable
 |
 v
Wait
```

If the workflow timeout starts too early, the workflow might time out before the model even gets to execute.

Then:

```text
Workflow timeout
       |
       v
Retry
       |
       v
Potential duplicate execution
```

Your current system mitigates this by monitoring queue depth and dynamically provisioning enough CPU/GPU capacity.

Conceptually:

```text
Queue depth
    |
    v
Capacity controller
    |
    v
More CPU/GPU nodes
    |
    v
Queue drains
```

This reduces capacity-induced timeouts, although it doesn't mathematically eliminate every duplicate-execution scenario.

---

# 3.20 Why not choreography?

An interviewer might ask:

> "Why not just let services call each other?"

The answer is not:

> "Because choreography needs compensation."

That's too broad.

Your actual reason is:

The workflow contains:

* many ordered steps
* dependencies
* conditional execution
* retries
* timeouts
* long-running operations
* workflow state
* replay
* external waiting
* expensive tasks

Therefore, centralized orchestration was more appropriate.

You can say:

> "We had a long-running, dependency-heavy workflow where we needed explicit workflow state, retries, timeouts, conditional execution and replay. Rather than distributing that state machine across many services, we centralized the workflow state in Conductor."

---

# 3.21 Why not one huge workflow?

The initial problem was actually the opposite.

You had:

```text
50 model workflows
```

and common behavior was duplicated.

The solution wasn't:

```text
One gigantic workflow containing every model
```

because that would create a different maintenance problem.

Instead:

```text
Stable common workflow
        |
        v
Dynamic model-specific workflow
```

This creates the right separation.

---

# 3.22 Architectural evolution

This is the cleanest way to tell the story.

### Version 1

```text
Model A -> complete workflow
Model B -> complete workflow
Model C -> complete workflow
...
```

Problem:

```text
Common logic duplicated
```

### Version 2

```text
             Common Workflow
                    |
             Model Selector
                    |
          +---------+---------+
          |         |         |
        Model A   Model B   Model C
        workflow  workflow  workflow
```

Benefits:

* common logic changed once
* model workflows independently versioned
* new model onboarding easier
* less duplication
* smaller blast radius
* clearer ownership

---

# 3.23 Best Staff-level framing

The strongest statement from this story is:

> **"We separated stable orchestration concerns from model-specific change."**

Or:

> **"The goal wasn't just to introduce a workflow engine. It was to create an orchestration abstraction where common platform behavior remained stable while model-specific workflows could evolve independently."**

That is much stronger than:

> "We used Netflix Conductor."

Conductor is the implementation detail.

The architectural decision is the real story.

---

# 3.24 Best interview summary

A strong 90-second answer:

> "We had a processing pipeline with tens of steps, including cheap prerequisite tasks and expensive long-running AI inference. We needed centralized state, dependencies, retries, timeouts and replay, so we used Netflix Conductor.
>
> Initially we created one complete workflow per model. That worked at first, but as we grew to dozens of models, common tasks were duplicated across workflows. A change to common behavior required updating many workflows and created consistency and deployment risk.
>
> I refactored that into a common orchestration workflow plus model-specific dynamic sub-workflows. The common workflow owns things like upload, de-identification, routing and downstream delivery. A selector uses the model ID to dynamically invoke a conventionally named sub-workflow such as `ICH_sub_workflow`. A new model therefore requires registering its own workflow rather than modifying the core orchestration.
>
> We also used workflow versioning, task-specific timeouts and retries, and correlation IDs for replay. We accepted at-least-once execution because the model was a black box and we couldn't guarantee exactly-once execution. To make replay safe, the inference path checked for an existing result and result publication used deterministic S3 paths based on the logical request.
>
> The main architectural benefit was that the orchestration core became stable while model-specific behavior could evolve independently."

---

# 4. Comparing the Three Stories

These three stories actually demonstrate **three different Staff-level skills**.

| Story             | Core problem                                      | Your architectural decision                           | Staff signal                   |
| ----------------- | ------------------------------------------------- | ----------------------------------------------------- | ------------------------------ |
| **HA/DR**         | Regional failures / mission-critical availability | Multi-region routing + durable S3 + async replication | Failure-domain thinking        |
| **Database**      | HA/scale vs compatibility/resource constraints    | PostgreSQL + workload isolation                       | Technology selection/tradeoffs |
| **Orchestration** | Workflow complexity + duplicated model workflows  | Common workflow + dynamic sub-workflows               | Abstraction/evolution          |

---

# 5. The deeper common theme

There is actually a common architectural philosophy across all three.

You repeatedly avoided solving a problem by simply adding a more complicated technology.

### HA

Instead of:

> "Make everything synchronously replicated everywhere."

You used:

```text
Local durability
+
Async replication
+
On-prem source retention
```

---

### Database

Instead of:

> "Use distributed SQL because we're multi-region."

You used:

```text
PostgreSQL
+
Workload isolation
+
Appropriate deployment boundaries
```

---

### Orchestration

Instead of:

> "Create one giant workflow."

You used:

```text
Stable common workflow
+
Dynamic model-specific workflows
```

So the underlying Staff-level principle is:

> **Use complexity where it solves a real requirement, but isolate that complexity behind clear boundaries.**

That's a very good theme to carry into the Whop interview.

---

# 6. The three stories in one interview narrative

If an interviewer asks broadly:

> "Tell me about some significant architecture work you've done."

You can connect them like this:

### Story 1 — Availability

> "I designed a multi-region architecture where regional failure didn't stop processing. Global Accelerator handled regional routing, S3 provided the durable result boundary, and cross-region replication provided asynchronous recovery."

### Story 2 — Data architecture

> "For the database layer, I evaluated distributed SQL databases but found that the operational and resource costs didn't fit our deployment model. We instead used PostgreSQL with workload isolation."

### Story 3 — Workflow architecture

> "For orchestration, we initially had a workflow per AI model, but that became difficult to maintain. I separated common orchestration from model-specific sub-workflows so the core workflow could remain stable while models evolved independently."

And the common thread is:

> **"In each case, the important decision wasn't choosing the most sophisticated technology. It was understanding the failure modes, workload and operational constraints and then designing the boundaries around them."**

That is probably the **most important message to internalize** before the interview.
