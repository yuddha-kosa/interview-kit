# GIN (Generalized Inverted Index) Full-Text Search

A GIN (Generalized Inverted Index) is designed to index multi-valued elements component-by-component (like words within a document string or keys inside a JSONB block). It functions exactly like the index appendix at the back of a textbook.

## 1. The Core Architecture

Instead of mapping a single data row to a text string value (like a standard B-Tree index), a GIN index splits the document apart, indexing each unique word independently and mapping it back to a list of matching row addresses.

```
Document Table Storage
+==============================================+
| Row ID (TID) | Raw Text Document Column      |
+--------------+-------------------------------+
| Row 1        | "The engineer built an app"   |
| Row 2        | "Fast apps need databases"    |
+==============================================+
```

```
GIN Inverted Index Internal Layout
+==============================================+
| Unique Lexeme Key | Posting List (Row IDs)   |
+-------------------+--------------------------+
| 'app'             | [ Row 1, Row 2 ]         |
| 'built'           | [ Row 1 ]                |
| 'databas'         | [ Row 2 ]                |
| 'engin'           | [ Row 1 ]                |
| 'fast'            | [ Row 2 ]                |
+==============================================+
```

---

## 2. Under the Hood Mechanics

1. **The Entry Tree:** The sorted unique tokens (lexemes) are organized in a highly optimized standard B-Tree called the Entry Tree. Looking up a specific word takes logarithmic O(log N) time.
2. **Posting Lists vs. Posting Trees:** Attached directly to each unique word key is its data reference list:
   * **Posting List:** A simple, compressed array of row IDs (TIDs) where the token appears.
   * **Posting Tree:** If a word becomes highly saturated (e.g., appearing in millions of rows), the array list becomes a bottleneck. GIN automatically converts that specific long array list into its own dedicated internal B-Tree of row IDs to keep lookup speeds fast.

---

## 3. Production SQL Blueprint with tsvector Integration

For maximum query scale, storing a dedicated `tsvector` column side-by-side with your raw document column is highly recommended. A `tsvector` stores text already parsed into normalized word stems (lexemes) with common stop-words removed.

By applying an explicit database trigger or a `GENERATED ALWAYS AS` computed column, Postgres handles text compilation automatically during writes, avoiding expensive text parsing operations during client reads.

```sql
-- 1. Create table with raw text column and a computed tsvector column
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    -- Automatically maintains tokenized stems on write
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '')) ||
        to_tsvector('english', coalesce(content, ''))
    ) STORED
);

-- 2. Construct the GIN index over the tokenized vector column
CREATE INDEX idx_articles_search ON articles USING gin(search_vector);

-- 3. Execute a hyper-fast query matching multi-word tokens
SELECT title, content FROM articles WHERE search_vector @@ to_tsquery('english', 'apps & built');
```

**Query Phase Execution Steps:**

1. The app issues a `to_tsquery('apps & built')`. Postgres normalizes the tokens down to their structural stems: `'app'` & `'built'`.
2. It executes a binary search over the GIN index Entry Tree to find `'app'`, extracting its posting list: `[Row 1, Row 2]`.
3. It performs a parallel search over the tree to locate `'built'`, extracting its posting list: `[Row 1]`.
4. It completes a fast bitwise intersection algorithm on the arrays in RAM: `[Row 1, Row 2] AND [Row 1] = [Row 1]`.
5. It fetches Row 1 directly from disk pages, bypassing 99% of the unmatched records in the table.
