# Indexes
Learn about indexes in Materialize.
## Overview

Materialize indexes maintain the full result set of the indexed object in
the memory of the [cluster](/concepts/clusters/) where the index is created.
The cluster's workers keep the indexed results up-to-date as new data
arrives. Like clustered[^db-term] hash indexes, Materialize indexes store
the indexed results themselves and are efficient for equality lookups on the
full index key. Materialize indexes are not themselves hash indexes; hashing
is used only to distribute the index across the cluster's workers.

![Materialize index maintains the full result set in memory](/images/indexes/index_in_memory.svg)

Materialize indexes are **not** secondary indexes that store the index keys
and pointers to data rows.

![Materialize indexes do not use a key-pointer structure.](/images/indexes/index_not_key_pointer.svg)

[^db-term]: The term *clustered
index* is a database term unrelated to Materialize clusters, which are
compute resources.

## Creating indexes on objects

In Materialize, you can create indexes on [views](/concepts/views/#views) and
[materialized views](/concepts/views/#materialized-views) as well as on
[sources, tables, and subsources](/concepts/sources/).

To create indexes on an object, use the [`CREATE INDEX`](/sql/create-index/)
command. To create the index in a cluster other than the active cluster, include
the `IN CLUSTER` clause in the `CREATE INDEX` statement.

<no value>```mzsql
CREATE INDEX [<index_name>]
[IN CLUSTER <cluster_name>]
ON <obj_name> [USING <method>] (<col_expr>, ...)
[WITH (<with_options>)];

```

See [`CREATE INDEX`](/sql/create-index/) for the syntax details.

### Indexes on sources, tables, and subsources

> **Note:** In practice, you may find that you rarely need to index a source and its tables
> or subsources without performing some transformation using a view, etc.

In Materialize, you can create indexes on [sources, tables, or
subsources](/concepts/sources/) to maintain up-to-date data in the memory of
the cluster where you create the index. This can help improve [query
performance](#indexes-and-query-optimizations), for example when [using
joins](/transform-data/optimization/#join) in your transformation. However, in
practice, you may find that you rarely need to index these objects directly.

```mzsql
CREATE INDEX idx_on_my_source_table ON my_source_table(...);
```

### Indexes on views

In Materialize, you can [create indexes](/sql/create-index/) on a
[view](/concepts/views/#views "query saved under a name") to maintain
**up-to-date view results in memory** within the [cluster](/concepts/clusters/)
where you create the index.

- To create the index in the current active cluster (you can use the `SET
  CLUSTER` command to change the active cluster):

  ```mzsql
  CREATE INDEX idx_on_my_view ON my_view_name(...);
  ```

- To create the index in a specified cluster:

  ```mzsql
  CREATE INDEX idx_on_my_view IN CLUSTER serving_cluster ON my_view_name(...);
  ```

During the index creation, the view is executed and the view results are stored
in memory within the cluster. **As new data arrives**, the index **incrementally
updates** the view results in memory.

Querying a view from a cluster where the view is indexed is **fast** because
the results are already computed and are served from memory. Querying a view
from a cluster where the view isn't indexed requires executing the view each
time you query it.

### Indexes on materialized views

In Materialize, materialized view results are stored in durable storage and
**incrementally updated** as new data arrives. [Indexing](/sql/create-index/) a
materialized view makes the already up-to-date view results available **in
memory** within the [cluster](/concepts/clusters/) where you create the index.
That is, indexes on materialized views require no additional computation to keep
results up-to-date.

> **Note:** A materialized view can be queried from any cluster whereas its indexed results
> are available only within the cluster where you create the index. Querying a
> materialized view from any cluster, whether the materialized view is indexed or
> not, is fast because the results are already computed. However, querying an
> indexed materialized view from a cluster where the materialized view is indexed
> is faster since the results are served from memory rather than from storage.

- To create the index in the current active cluster (you can use the `SET
  CLUSTER` command to change the active cluster):

  ```mzsql
  CREATE INDEX idx_on_my_mat_view ON my_mat_view_name(...);
  ```

- To create the index in a specified cluster:

  ```mzsql
  CREATE INDEX idx_on_my_mat_view IN CLUSTER serving_cluster ON my_mat_view_name(...);
  ```

## Properties

### Cluster-local

Indexes are accessible only from their own cluster. Indexed results reside
in the memory of the cluster where the index is created, and a [cluster's
memory](/concepts/clusters/#resource-isolation) cannot be accessed from
another cluster.
 As
such, references to the indexed object from a different cluster cannot use the
index.

### Data distribution and ordering

The index data is distributed across the cluster's
workers by a hash of the key, which spreads the maintenance and lookup work
across the cluster.

Within each worker, index keys are ordered by their internal representation
(the encoded key's length, then its bytes), not by the data types' natural
ordering.

### Serving ad-hoc queries

Within a cluster, all ad-hoc queries that reference an indexed object read from
the index, regardless of whether the index is optimized for the query. This
includes queries that do not specify a `WHERE` condition on the index key.
Because the indexed results are already up-to-date and in memory, reading from
an index avoids recomputing the results.

- **Point lookups**: For queries that specify an equality condition on the full
  index key, Materialize can perform a point lookup, reading only the matching
  records from the index. Point lookups are the most efficient use of an index.
  See [Point lookups](#point-lookups) for the exact requirements.

- **Index scans**: Otherwise, Materialize scans the index. Although the indexed
  results are already up-to-date and in memory, a full index scan must examine
  the indexed results and is less efficient than a point lookup. The performance
  of full index scans degrades with data volume.

### Index use by objects

<p>Within a cluster, an index can be used not only by ad-hoc queries but also
by other indexes and materialized views. For an index or materialized view
to use another index, however, that index must exist when the dependent
object is created. That is:</p>
<ul>
<li>
<p>When you create an index or a materialized view, Materialize plans how
to compute its results at creation time. As part of planning, Materialize
checks whether it can reuse an <strong>existing</strong> index in the <strong>same</strong>
cluster.</p>
</li>
<li>
<p>Because the plan is bound at creation time, creation order matters. An
index or materialized view that is already running will <strong>not</strong> adopt an
index created afterward. To have an existing index or materialized view
use a newer index, drop and recreate the existing object. However,
recreating an index or a materialized view triggers
<a href="/concepts/hydration/#when-hydration-occurs" >hydration</a>.</p>
</li>
</ul>
<p>Ad-hoc queries, by contrast, are planned at query time. They can use any
index that exists in the cluster when the query runs.</p>
> **Note:** Reusing an index saves computation since the dependent objects read the
> index's maintained results instead of recomputing them from the base data.
> However, each new index has costs related to cluster memory and ongoing
> maintenance, especially indexes on regular views.

To inspect index reuse and dependencies:

- To check whether a new index would reuse an existing index before creating
  it, use [`EXPLAIN CREATE INDEX`](/sql/explain-plan/).

- To find which indexes and materialized views use an index, query
  [`mz_internal.mz_materialization_dependencies`](/reference/system-catalog/mz_internal/#mz_materialization_dependencies).

### Limitations

<p>Materialize indexes are not optimized for:</p>
<ul>
<li>
<p>Ordered access, including:</p>
<ul>
<li>
<p>Range queries, that is, queries using <code>&gt;</code>, <code>&gt;=</code>, <code>&lt;</code>, <code>&lt;=</code>, or <code>BETWEEN</code>
(e.g., <code>WHERE quantity &gt; 10</code>, <code>WHERE price &gt;= 10 AND price &lt;= 50</code>, and
<code>WHERE quantity BETWEEN 10 AND 20</code>).</p>
</li>
<li>
<p>Queries that use <code>ORDER BY</code> on the index key.</p>
</li>
</ul>
</li>
<li>
<p>Lookups on a prefix of a multi-column index key. For example, an index
with the key <code>(a, b)</code> is not optimized for a query that specifies an
equality condition on <code>a</code> but not on <code>b</code>.</p>
</li>
<li>
<p>Lookups that do not match the exact index key expression. For example,
for an index with the key <code>lower(a)</code>, an equality condition on <code>a</code> does
not match the index key; the query must specify an equality condition on
<code>lower(a)</code> for a point lookup.</p>
</li>
<li>
<p><code>GROUP BY</code> aggregations. An index on the grouping key does not reduce the work of computing the aggregation: Materialize reads the full index and maintains the aggregation separately.</p>
</li>
</ul>

## Point lookups vs index scans

### Point lookups

Point lookups read just the matching records from the index and are the most
efficient use of an index. Materialize performs a point lookup if the query's
`WHERE` clause:

- Specifies equality (`=` or `IN`) condition and **only** equality conditions on
  **all** the indexed fields. The equality conditions must specify the **exact**
  index key expression (including type) for point lookups. For example:

  - If the index is on `round(quantity)`, the query must specify equality
    condition on `round(quantity)` (and not just `quantity`) for Materialize to
    perform a point lookup.

  - If the index is on `quantity * price`, the query must specify equality
    condition on `quantity * price` (and not `price * quantity`) for Materialize
    to perform a point lookup.

  - If the index is on the `quantity` field which is an integer, the query must
    specify an equality condition on `quantity` with a value that is an integer.

- Only uses `AND` (conjunction) to combine conditions for **different** fields.

For queries whose `WHERE` clause meets the point lookup criteria and includes
conditions on additional fields (also using `AND` conjunction), Materialize
performs a point lookup on the index keys and then filters the results using the
additional conditions on the non-indexed fields.

### Index scans

For queries that do not meet the [point lookup criteria](#point-lookups),
Materialize performs a full index scan (including for range queries). That is,
Materialize performs a full index scan if the `WHERE` clause:

- Does not specify **all** the indexed fields.
- Does not specify only equality conditions on the index fields or specifies an
  equality condition that specifies a different value type than the index key
  type.
- Uses `OR` (disjunction) to combine conditions for **different** fields.

Full index scans are less efficient than point lookups. The performance of full
index scans will degrade with data volume; i.e., as you get more data, full
scans will get slower.

### Examples

Within a cluster, indexes can serve queries that reference an indexed object,
regardless of whether the index is optimized for the query.

Consider the following index on the `orders_view`:

```mzsql
CREATE INDEX idx_orders_view_qty ON orders_view (quantity);
```

Materialize can use the index to serve various queries on the `orders_view`
(and not just queries that specify conditions on `orders_view.quantity`). For
example:

```mzsql
SELECT * FROM orders_view;  -- scans the index
SELECT * FROM orders_view WHERE status = 'shipped';  -- scans the index
SELECT * FROM orders_view WHERE quantity = 10;  -- point lookup on the index
```

For the queries that do not satisfy the [point-lookup
conditions](#point-lookups), Materialize scans the index.

The following table shows various queries and whether Materialize performs a
point lookup or an index scan.

| Query | Index Usage |
| --- | --- |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span><span class="p">;</span> </span></span></code></pre></div> | Point lookup. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="k">IN</span> <span class="p">(</span><span class="mf">10</span><span class="p">,</span> <span class="mf">20</span><span class="p">);</span> </span></span></code></pre></div> | Point lookup. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">OR</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">20</span><span class="p">;</span> </span></span></code></pre></div> | Point lookup. Query uses <code>OR</code> to combine conditions on the <strong>same</strong> field. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">AND</span> <span class="n">price</span> <span class="o">=</span> <span class="mf">5.00</span><span class="p">;</span> </span></span></code></pre></div> | Point lookup on <code>quantity</code>, then filter on <code>price</code>. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="p">(</span><span class="n">quantity</span><span class="p">,</span> <span class="n">price</span><span class="p">)</span> <span class="o">=</span> <span class="p">(</span><span class="mf">10</span><span class="p">,</span> <span class="mf">5.00</span><span class="p">);</span> </span></span></code></pre></div> | Point lookup on <code>quantity</code>, then filter on <code>price</code>. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">OR</span> <span class="n">price</span> <span class="o">=</span> <span class="mf">5.00</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. Query uses <code>OR</code> to combine conditions on <strong>different</strong> fields. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">&lt;=</span> <span class="mf">10</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">round</span><span class="p">(</span><span class="n">quantity</span><span class="p">)</span> <span class="o">=</span> <span class="mf">20</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Assume quantity is an integer </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="s1">&#39;hello&#39;</span><span class="p">;</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span><span class="o">::</span><span class="nb">TEXT</span> <span class="o">=</span> <span class="s1">&#39;hello&#39;</span><span class="p">;</span> </span></span></code></pre></div> | Index scan, assuming <code>quantity</code> field in <code>orders_view</code> is an integer. In the first query, the quantity is implicitly cast to text. In the second query, the quantity is explicitly cast to text. |

Consider that the view has an index on the `quantity` and `price` fields
instead of an index on the `quantity` field:

```mzsql
DROP INDEX idx_orders_view_qty;
CREATE INDEX idx_orders_view_qty_price on orders_view (quantity, price);
```

| Query | Index Usage |
| --- | --- |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. Query does not include equality conditions on <strong>all</strong> indexed fields. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">AND</span> <span class="n">price</span> <span class="o">=</span> <span class="mf">2.50</span><span class="p">;</span> </span></span></code></pre></div> | Point lookup. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> <span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">OR</span> <span class="n">price</span> <span class="o">=</span> <span class="mf">2.50</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. Query uses <code>OR</code> to combine conditions on <strong>different</strong> fields. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">AND</span> <span class="p">(</span><span class="n">price</span> <span class="o">=</span> <span class="mf">2.50</span> <span class="k">OR</span> <span class="n">price</span> <span class="o">=</span> <span class="mf">3.00</span><span class="p">);</span> </span></span></code></pre></div> | Point lookup. Query uses <code>OR</code> to combine conditions on <strong>same</strong> field and <code>AND</code> to combine conditions on <strong>different</strong> fields. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">AND</span> <span class="n">price</span> <span class="o">=</span> <span class="mf">2.50</span> <span class="k">AND</span> <span class="n">item</span> <span class="o">=</span> <span class="s1">&#39;cupcake&#39;</span><span class="p">;</span> </span></span></code></pre></div> | Point lookup on the index keys <code>quantity</code> and <code>price</code>, then filter on <code>item</code>. |
| <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders_view</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">quantity</span> <span class="o">=</span> <span class="mf">10</span> <span class="k">AND</span> <span class="n">price</span> <span class="o">=</span> <span class="mf">2.50</span> <span class="k">OR</span> <span class="n">item</span> <span class="o">=</span> <span class="s1">&#39;cupcake&#39;</span><span class="p">;</span> </span></span></code></pre></div> | Index scan. Query uses <code>OR</code> to combine conditions on <strong>different</strong> fields. |

## Usage

### Indexes on views vs. materialized views

In Materialize, both [indexes](/concepts/indexes) on views and [materialized
views](/concepts/views/#materialized-views) incrementally update the view
results when Materialize ingests new data. Whereas materialized views persist
the view results in durable storage and can be accessed across clusters, indexes
on views compute and store view results in memory within a **single** cluster.

Some general guidelines for usage patterns include:

| Usage Pattern | General Guideline |
|--------------------------------------------------------------------------------|--------------------|
| View results are accessed from a single cluster only;<br>such as in a 1-cluster or a 2-cluster architecture. | View with an [index](/sql/create-index) |
| View used as a building block for stacked views; i.e., views not used to serve results. | View |
| View results are accessed across [clusters](/concepts/clusters);<br>such as in a 3-cluster architecture. | Materialized view (in the transform cluster)<br>Index on the materialized view (in the serving cluster) |
| Use with a [sink](/serve-results/sink/) or a [`SUBSCRIBE`](/sql/subscribe) operation | Materialized view  |
| Use with [temporal filters](/transform-data/patterns/temporal-filters/) | Materialized view  |

<p>For example:</p>

**3-tier architecture:**

![Image of the 3-tier-architecture
architecture](/images/3-tier-architecture.svg)

In a [3-tier
architecture](/manage/operational-guidelines/#three-tier-architecture)
where queries are served from a cluster different from the compute/transform
cluster that maintains the view results:

- Use materialized view(s) in the compute/transform cluster for the query
  results that will be served.

  If you are using <strong>stacked views</strong> (i.e., views whose definition depends
  on other views) to reduce SQL complexity, generally, only the topmost
  view (i.e., the view whose results will be served) should be a
  materialized view. The underlying views that do not serve results do not
  need to be materialized.

- Index the materialized view in the serving cluster(s) to serve the results
from memory.

**2-tier architecture:**

![Image of the 2-tier-architecture](/images/2-tier-architecture.svg)

In a [2-tier
architecture](/manage/appendix-alternative-cluster-architectures/#two-tier-architecture)
where queries are served from the same cluster that performs the
compute/transform operations:

- Use view(s) in the shared cluster.

- Index the view(s) to incrementally update the view results and serve the
results from memory.

> **Tip:** Except for when used with a [sink](/serve-results/sink/),
> [subscribe](/sql/subscribe/), or [temporal
> filters](/transform-data/patterns/temporal-filters/), avoid creating
> materialized views on a shared cluster used for both compute/transform
> operations and serving queries. Use indexed views instead.

**1-tier architecture:**

![Image of the 1-tier-architecture](/images/1-tier-architecture.svg)

In a [1-tier
architecture](/manage/appendix-alternative-cluster-architectures/#one-tier-architecture)
where queries are served from the same cluster that performs the
compute/transform operations:

- Use view(s) in the shared cluster.

- Index the view(s) to incrementally update the view results and serve the
results from memory.

> **Tip:** Except for when used with a [sink](/serve-results/sink/),
> [subscribe](/sql/subscribe/), or [temporal
> filters](/transform-data/patterns/temporal-filters/), avoid creating
> materialized views on a shared cluster used for both compute/transform
> operations and serving queries. Use indexed views instead.

### Indexes and query optimizations

By making up-to-date results available in memory, indexes can help [optimize
query performance](/transform-data/optimization/), such as:

- Provide faster sequential access than unindexed data.

- Provide fast random access for lookup queries (i.e., selecting individual
  keys).

Specific instances where indexes can be useful to improve performance include:

- When used in ad-hoc queries.

- When used by multiple queries within the same cluster.

- When used to enable [delta
  joins](/transform-data/optimization/#optimize-multi-way-joins-with-delta-joins).

For more information, see [Optimization](/transform-data/optimization).

### Best practices

Before creating an index, consider the following:

- If you create stacked views (i.e., views that depend on other views) to
  reduce SQL complexity, we recommend that you create an index **only** on the
  view that will serve results, taking into account the expected data access
  patterns.

- Materialize can reuse indexes across queries that concurrently access the same
  data in memory, which reduces redundancy and resource utilization per query.
  In particular, this means that joins do **not** need to store data in memory
  multiple times.

- For queries that have no supporting indexes, Materialize uses the same
  mechanics used by indexes to optimize computations. However, since this
  underlying work is discarded after each query run, take into account the
  expected data access patterns to determine if you need to index or not.

## Related pages

- [Optimization](/transform-data/optimization)
- [Views](/concepts/views)
- [`CREATE INDEX`](/sql/create-index)

<style>
red { color: Red; font-weight: 500; }
</style>
