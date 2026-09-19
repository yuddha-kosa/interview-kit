# Inverted Index

An inverted index is the foundational data structure used by search engines (like Elasticsearch, Apache Lucene, and Google) to make full-text search incredibly fast.

Instead of searching through documents for words (like reading a book page-by-page), it maps words to the documents they appear in (like the index at the back of a textbook).

---

## Direct Comparison: Forward Index vs. Inverted Index

To understand why it is called "inverted," look at how it flips traditional database storage:

| Feature | Forward Index (Standard DB / Document Store) | Inverted Index (Search Engine) |
|---|---|---|
| Core Structure | Document → Words | Word → Documents |
| How it works | Stores a document and lists all the words inside it. | Stores a distinct word and lists all document IDs containing it. |
| Best Used For | Fetching a specific document by its ID (e.g., Get Document #3). | Searching for a specific keyword across millions of files. |
| Search Speed | Slow O(N). Requires scanning every word of every document (linear scan). | Blazing fast O(1) or O(log N). Instantly jumps to the word. |

---

## Step-by-Step Architecture: How It Is Built

Imagine you have three simple documents in your database:

* Doc 1: "I love system design"
* Doc 2: "Design patterns are great"
* Doc 3: "I love design patterns"

### Step 1: Tokenization and Text Normalization

The search engine processes the text by breaking sentences into individual words (tokens), converting everything to lowercase, and removing punctuation.

### Step 2: Inverting the Structure

The system creates a global table. The distinct words become the keys (called terms), and the values become a list of matching document locations (called postings lists):

| Term (Key) | Postings List (Matching Doc IDs) |
|---|---|
| are | [2] |
| design | [1, 2, 3] |
| great | [2] |
| love | [1, 3] |
| patterns | [2, 3] |
| system | [1] |

---

## How Search Queries Execute Instantly

If a user searches for "love design":

1. The search engine splits the query into two terms: `love` and `design`.
2. It instantly fetches the postings lists for both keys:
   * `love` → `[1, 3]`
   * `design` → `[1, 2, 3]`
3. It performs a highly optimized set intersection (AND logic) or set union (OR logic) on those lists:
   * `[1, 3] ∩ [1, 2, 3] = [1, 3]`
4. The engine immediately returns Document 1 and Document 3 to the user without touching Document 2.

---

## Interview-Level Deep Dive: Scale and Memory Challenges

In a real system design interview, storing a raw table like this across billions of documents causes scaling challenges. Search engines optimize this structure using two sub-components:

* **The Term Dictionary:** The column of words (keys). Because there are millions of unique words, this dictionary is sorted alphabetically and stored in memory using compressed data structures like Finite State Transducers (FST) or B-Trees so the system can find a word in microseconds.
* **The Postings Lists:** The list of doc IDs (values). These arrays grow massive. Engines use bitmask compression techniques (like Frame of Reference or Roaring Bitmaps) to shrink the list of integers on disk and accelerate the mathematical intersection math during a search.
