# Back-of-the-Envelope Capacity Estimation: The Zeros and Commas Shortcut

To quickly calculate back-of-the-envelope capacity numbers during a system design interview, use the Zeros and Commas Shortcut.

In an interview setting, trying to divide exactly by 1,024 or 1,073,741,824 mentally will slow you down and lead to math errors. Instead, treat 1 KB as exactly 1,000 bytes (using base-10). This approximation is universally accepted by interviewers for quick estimations.

---

## The Cheat Sheet Rules

Memorize how the scale of your rows (the number of zeros) multiplies against a single byte unit:

* Bytes × Thousands (10³ / 3 zeros / 1 K) → KB (Kilobytes)
* Bytes × Millions (10⁶ / 6 zeros / 1 M) → MB (Megabytes)
* Bytes × Billions (10⁹ / 9 zeros / 1 B) → GB (Gigabytes)
* Bytes × Trillions (10¹² / 12 zeros / 1 T) → TB (Terabytes)

---

## Walking Through an Example

The Problem: 1 billion rows, 500 bytes each.

### Step 1: Write Down the Multiplication

```
Total Capacity = 1,000,000,000 × 500 bytes
```

### Step 2: Swap the Scale Word for Its Corresponding Unit Label

Look at the cheat sheet: Billion maps directly to GB. You can instantly drop the word "Billion" and attach "GB" to the remaining math numbers:

```
1 × 500 bytes → 500 GB
```

---

## Two More Practice Examples

### Scenario A: High-Throughput Log Data

* The Problem: 100 million rows per day, 200 bytes per row.
* The Shortcut: Million maps directly to MB.
* The Math: 100 × 200 = 20,000 MB.
* Simplify: Since 1,000 MB = 1 GB, shift the decimal point left by three spots → 20 GB per day.

### Scenario B: Giant Analytical Data Warehouse

* The Problem: 10 billion profile rows, 1 KB (1,000 bytes) per row.
* The Shortcut: Billion maps directly to GB.
* The Math: 10 × 1,000 = 10,000 GB.
* Simplify: Since 1,000 GB = 1 TB, shift the decimal point left by three spots → 10 TB total storage.

---

## Summary Note for Your System Design Notebook

Keep this quick reference block at the top of your practice scratchpad:

```
[Scale of Rows]  x  [Unit Size]  =  [Resulting Sizing]
------------------------------------------------------
Millions (M)     x  Bytes        =  MB
Billions (B)     x  Bytes        =  GB
Trillions (T)    x  Bytes        =  TB
```

* If your unit size is already in KB, shift the final answer up by one tier (e.g., Billions × KB = TB).

---

## Sanity Check: Decimal vs. Binary Units

The shortcut above uses decimal (base-10) units, which is what interviewers expect. For reference, here's the exact math showing the gap against true binary (base-2) units:

```python
rows = 1_000_000_000
bytes_per_row = 500
total_bytes = rows * bytes_per_row

gb_decimal = total_bytes / (10 ** 9)   # decimal GB (interview shortcut)
gib_binary = total_bytes / (2 ** 30)   # true binary GiB

print(f"Decimal GB: {gb_decimal}, Binary GiB: {gib_binary}")
```

```
Decimal GB: 500.0, Binary GiB: 465.66
```

The ~7% gap between GB and GiB is small enough to ignore for interview-level estimation, but know it exists if asked to be precise.
