# PostgreSQL Transaction Isolation Levels & Concurrency Control

PostgreSQL implements transaction isolation levels using Multi-Version Concurrency Control (MVCC). Instead of using raw read-locks that block writers, Postgres appends new versions of row tuples directly into the physical page heap file, determining visibility dynamically using hidden metadata parameters.

## Structural Tuple Metadata Parameters

Every physical row version (tuple) in the Postgres heap contains internal transaction visibility attributes:

* **xmin:** The transaction ID (TxID) of the transaction that inserted the row.
* **xmax:** The TxID of the transaction that updated or deleted the row. If the row is alive, `xmax = 0`.

When a row is updated, the original tuple has its `xmax` set to the current transaction ID, and a completely fresh version of the tuple is appended into the heap page file with its `xmin` set to that same transaction ID.

---

## 1. Read Committed (Default Level)

* **The Rule:** Each query statement within a transaction establishes a brand-new snapshot, ensuring it only sees data committed before that specific query statement started execution.
* **Conflict Mechanic (EvalPlanQual):** If two concurrent transactions attempt to modify the same row, the second transaction blocks and sleeps until the first transaction commits or aborts.

### Scenario & Re-evaluation Trace

Initial State: `Tuple V1 [Price: $10 | xmin: 90 | xmax: 0]`

* Transaction 1 (TxID 101): Updates the price to $12. Tuple V1's `xmax` is set to 101. Tuple V2 is appended `[Price: $12 | xmin: 101 | xmax: 0]`. T1 commits.
* Transaction 2 (TxID 102): Concurrently issues `UPDATE products SET price = 15 WHERE id = 1;` while T1 is processing.

```
                     [ HEAP STORAGE AREA ]
+-------------------------------------------------------------+
| Tuple V1 (Old)   -> [Price: $10 | xmin: 90  | xmax: 101]    | (Dead)
|   | (Chain Pointer)                                         |
|   v                                                         |
| Tuple V2 (T1)    -> [Price: $12 | xmin: 101 | xmax: 102]    | (Dead)
|   | (Chain Pointer)                                         |
|   v                                                         |
| Tuple V3 (T2)    -> [Price: $15 | xmin: 102 | xmax: 0]      | (Alive & Committed)
+-------------------------------------------------------------+
```

1. T2 attempts to access Tuple V1, sees `xmax = 101`, and pauses.
2. T1 commits. T2 wakes up. Because it operates under Read Committed, it is allowed to see T1's changes mid-flight.
3. T2 triggers EvalPlanQual (EPQ). It follows the row version chain pointers from the dead Tuple V1 straight down to Tuple V2.
4. T2 re-checks its `WHERE` filters against Tuple V2. If it still matches, T2 applies its update directly on top of Tuple V2 rather than overwriting it, outputting Tuple V3. No data is lost or blindly overwritten.

---

## 2. Repeatable Read

* **The Rule:** The transaction locks in a single, unchangeable data snapshot the exact millisecond its very first query begins. It will never see any commits made by other transactions after its start timestamp.
* **Conflict Mechanic (First-Committer-Wins):** It blocks concurrent modifications using strict serialization assertions rather than mid-flight re-evaluation.

### Scenario & Crash Trace

Initial State: `Tuple V1 [Price: $10 | xmin: 90 | xmax: 0]`

1. T1 (TxID 101) and T2 (TxID 102) open their snapshots concurrently. Both see Tuple V1 perfectly.
2. T1 executes an update modifying the row, sets Tuple V1's `xmax` to 101, appends Tuple V2, and commits.
3. T2 wakes up from its pause state and attempts to run an update on that same row identity.
4. **The Visibility Check Failure:** T2 realizes the row was updated by TxID 101. It checks its snapshot visibility rules and finds that TxID 101 committed after T2's snapshot frozen time window started.
5. Rather than risking a lost update by overwriting Tuple V2, Postgres immediately aborts T2 and kills it with a serialization failure error:

```
ERROR: could not serialize access due to concurrent update
```

* **Limitation (Write Skew Anomaly):** Repeatable Read only protects data at the individual row level. If two transactions read a shared condition but modify different rows based on that condition, no `xmax` conflicts occur. Both commit successfully, breaking cross-row logical constraints.

---

## 3. Serializable

* **The Rule:** Transactions execute with a guarantee that the end state matches a sequence where transactions ran strictly one after another.
* **Conflict Mechanic (SIREAD Locks):** Extends Repeatable Read by maintaining non-blocking, invisible SIREAD lock tags in memory that track transaction read dependencies.

### Scenario & Write Skew Prevention Trace (Doctor On-Call Rule)

Business Constraint: "At least one doctor must be active on-call at all times."
Initial State: Doctor Alice (active=true), Doctor Bob (active=true).

```
T1 (Alice's Transaction)                       T2 (Bob's Transaction)
------------------------                       ----------------------
BEGIN (SERIALIZABLE);                          BEGIN (SERIALIZABLE);

SELECT COUNT(*) WHERE active=true;             SELECT COUNT(*) WHERE active=true;
--> Returns 2. Safe to check out.              --> Returns 2. Safe to check out.
(Leaves SIREAD tag on both rows)               (Leaves SIREAD tag on both rows)

UPDATE shift SET active=false                  UPDATE shift SET active=false
WHERE name = 'Alice';                          WHERE name = 'Bob';

COMMIT; -> Success!
                                               COMMIT; -> CRASHES INSTANTLY!
                                               (Postgres analyzes SIREAD graph tags,
                                                realizes T2 wrote to a dependency state
                                                that T1 altered, and aborts T2.)
```
