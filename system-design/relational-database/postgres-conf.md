# PostgreSQL Memory Configuration for Production

You cannot change the underlying 8KB physical page size via config, but PostgreSQL has several memory parameters you can — and should — tune in production.

Default Postgres settings are intentionally conservative so the database can boot on tiny, low-resource machines. In production, tuning these is essential to avoid performance bottlenecks.

---

## 1. `shared_buffers` — the data cache size

The single most important memory parameter. It dictates how much RAM Postgres allocates to cache 8KB heap and index pages.

- **Default:** ~128 MB.
- **If too small:** every query has to physically read 8KB pages from slow disk instead of pulling them from RAM.
- **Production recommendation:** set to 25% of total system RAM on dedicated database servers (e.g., 32GB RAM → `shared_buffers = 8GB`).

## 2. `work_mem` — the query operation sorting size

The maximum size of a temporary memory area allocated to a single sort or hash operation inside a query (`ORDER BY`, `DISTINCT`, heavy `JOIN`).

- **Default:** 4 MB.
- **If a query exceeds this:** Postgres pauses, creates a temporary swap file on disk, dumps the data there to finish the sort, and reads it back. This destroys query performance.
- **The production danger:** this memory is allocated per operation, per query, per user. 100 users running a query with 3 sort operations means `100 × 3 × work_mem`. Setting this too high can exhaust memory and crash the server.
- **Production recommendation:** start conservatively at 32–64MB globally. Temporarily raise it for individual heavy reporting sessions without changing the global setting:

  ```sql
  SET LOCAL work_mem = '256MB';
  SELECT * FROM massive_table ORDER BY total_sales;
  ```

## 3. `maintenance_work_mem` — the database maintenance size

Memory allowed for maintenance tasks — building indexes (`CREATE INDEX`) or running `VACUUM`.

- **Default:** 64 MB.
- **Production recommendation:** since maintenance tasks usually run one at a time via background workers, this can be set much higher than `work_mem`. Allocate roughly 10% of system RAM, up to 2–4GB. This speeds up index creation and prevents `VACUUM` from stalling.

## 4. `max_wal_size` — the transaction log file size

Postgres writes every transaction sequentially to the WAL before modifying the database. `max_wal_size` bounds how large these log files can grow before Postgres forces an internal checkpoint.

- **Default:** 1 GB.
- **If too small:** on a busy write-heavy application, WAL files fill up rapidly. Once the limit hits, Postgres triggers an aggressive "emergency checkpoint," forcing data out of RAM to disk and causing I/O lag spikes.
- **Production recommendation:** for high-volume write databases, increase to 16–32GB. This spaces out checkpoints and gives stable, predictable disk performance.

## How to apply these in production

Open `postgresql.conf`, locate the parameters, change the sizes (using `MB`/`GB` units), and restart the Postgres service.

For a safe starting point tailored to your hardware, use [PGTune](https://pgtune.leopard.in.ua/) — input your server's total RAM, CPU count, and application type, and it generates recommended values for these parameters.

---

# Diagnosing Memory Config Issues via Logs

PostgreSQL will log emergency storage operations, though the exact message depends on whether you're running out of query operation memory (`work_mem`) or transaction log space (`max_wal_size`).

## 1. `work_mem` too small (disk spilling)

When a sort/hash operation exceeds `work_mem`, Postgres creates temporary swap files on disk — "spilling to disk." Enable logging in `postgresql.conf`:

```ini
log_temp_files = 0  # 0 means log ALL temporary files created
```

Log output:

```text
LOG:  temporary file: path "base/pgsql_tmp/pgsql_tmp12345.0", size 45875200 bytes
STATEMENT:  SELECT * FROM users ORDER BY total_purchases DESC;
```

**How to read this:** check the `size` field (in bytes). A size of 45875200 bytes (~45 MB) means Postgres had to write 45 MB of temporary sorting data to disk because `work_mem` was too small to hold it.

## 2. `max_wal_size` too small (aggressive checkpoints)

If write traffic spikes and `max_wal_size` is too low, WAL files fill up too quickly, forcing an emergency, unscheduled checkpoint. Enable checkpoint logging:

```ini
log_checkpoints = on
```

Log output:

```text
WARNING:  checkpoints are occurring too frequently (every 12 seconds)
HINT:  Consider increasing the configuration parameter "max_wal_size".
```

**How to read this:** checkpoints should happen at a relaxed pace (every 5–15 minutes, per `checkpoint_timeout`). A warning that they're occurring every few seconds means the write pipeline is suffering severe I/O stalls from repeated emergency disk flushes.

## 3. `shared_buffers` too small (hidden metric)

If `shared_buffers` is too small, Postgres doesn't print an emergency error — the database silently slows down as it keeps discarding pages from RAM and re-fetching them from disk.

To detect this, query `pg_stat_database`:

```sql
SELECT datname, blks_read, blks_hit,
       (blks_hit::float / (blks_hit + blks_read + 1) * 100) AS cache_hit_ratio
FROM pg_stat_database;
```

- `blks_hit`: 8KB pages read directly from the `shared_buffers` RAM cache (fast).
- `blks_read`: pages fetched from physical disk because they weren't in memory (slow).
- `cache_hit_ratio`: in a healthy production environment, this should be 99%+. A ratio below 95% is strong evidence that `shared_buffers` is too small for the active dataset.
