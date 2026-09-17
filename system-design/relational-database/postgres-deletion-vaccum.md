# Does a Deleted Row's Space Get Reused Immediately?

No — a next `INSERT` or `UPDATE` cannot use that space immediately. A `VACUUM` must run first.

Until `VACUUM` scans that page, the space occupied by the deleted row remains locked up and unusable for new data.

---

## 1. Why a new insert can't use the space immediately

When you delete a row, Postgres only changes the row's metadata (`xmax = <transaction ID>`).

- The engine can't safely let another query overwrite that space right away, because concurrent transactions might still be actively reading it.
- Postgres pages are strictly formatted — the layout doesn't automatically shift or shrink when a row is marked dead. It requires an intentional administrative sweep to mark those bytes as "empty."

If you delete a 1KB row and immediately run a new `INSERT`, Postgres bypasses that dead row's page entirely and looks for space elsewhere in the Heap file — even if that means expanding the file.

---

## 2. Does `VACUUM` delete the dead row permanently?

Yes, with a catch regarding physical disk space.

When `VACUUM` runs, it checks: are there any active transactions still running that started before this row was deleted?

- If no, `VACUUM` permanently removes the dead data from that 8KB page.
- It records the exact starting byte and size of the newly opened slot into the **Free Space Map (FSM)**.

The next `INSERT` or `UPDATE` checks the FSM first, finds the empty slot left behind, and writes the new data directly into that space. Your table stops growing in size.

---

## 3. The catch: what `VACUUM` does *not* do

While `VACUUM` permanently deletes the dead row from the page, it does **not** return that disk space back to the operating system.

If your table file is 10 GB and you delete 5 GB of rows, then run a standard `VACUUM`:

- The file on disk is still 10 GB.
- The 5 GB is simply cleared *inside* the file, like an empty parking lot waiting for your next inserts.

### Returning space to the OS

To shrink the actual file size after a massive deletion, run:

```sql
VACUUM FULL my_table;
```

Unlike regular `VACUUM` (which runs quietly in the background via autovacuum), `VACUUM FULL` completely locks the table:

- It creates a brand-new, empty file on disk.
- It copies only the live, active rows into the new file.
- It deletes the old, bloated file entirely.
- The application cannot read or write to that table while this runs. In production, this should only be done during scheduled maintenance windows.

---

## Summary

- New inserts cannot use a deleted row's space immediately.
- A background `VACUUM` must run first to clear the row and log the empty slot into the Free Space Map.
- Once logged, future inserts reuse that space, preventing table growth.
- The physical file on disk only shrinks if you run a table-locking `VACUUM FULL`.
