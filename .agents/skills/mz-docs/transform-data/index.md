# Overview

Learn how to efficiently transform data using Materialize SQL.

With Materialize, you use SQL to transform your fast-changing data into **live
data products**: the business objects (e.g., a customer, an order, a store) that
your applications, services, dashboards, and AI agents read.

## From SQL to live data products

You use [views](/fundamentals/concepts/views/) and [materialized
views](/fundamentals/concepts/views/#materialized-views) to define your business objects in
SQL. Materialize keeps the results of **indexed views** and **materialized
views** up to date as it ingests your data.

Structuring your transformations as views gives you:

- **Reuse:** define a query once, then reference it from multiple places.
- **Readability:** save complex logic under a clear, meaningful name.
- **Composability:** break complex logic into stacked view definitions, building
  richer business objects on top of simpler ones.
- **Efficiency:** project only the columns you need, filter out unnecessary
  rows, and convert values to more [compact data types](/sql/types/) where
  possible.

## SQL in Materialize

Materialize follows the SQL standard (SQL-92) implementation and aims for
compatibility with the PostgreSQL dialect. It **does not** aim for
compatibility with a specific version of PostgreSQL. This means that
Materialize might support syntax from any released PostgreSQL version, but does
not provide full coverage of the PostgreSQL dialect. The implementation and
performance of specific features (like [window functions](/transform-data/idiomatic-materialize-sql/appendix/window-function-to-materialize))
might also differ, because Materialize uses an entirely different database
engine based on [Timely and Differential Dataflow](/fundamentals/#incremental-updates).

If you need specific syntax or features that are not currently supported in
Materialize, please submit a [feature request](https://materialize.com/support/).

## Explore this section

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    Write idiomatic SQL
  </div>
  <ul>
<li><a href="/transform-data/idiomatic-materialize-sql/" >Idiomatic Materialize SQL</a></li>
<li><a href="/transform-data/patterns/" >Common query patterns</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Optimize and operate
  </div>
  <ul>
<li><a href="/transform-data/optimization/" >Query optimization</a></li>
<li><a href="/transform-data/updating-materialized-views/" >Updating materialized views</a></li>
<li><a href="/fundamentals/concepts/indexes/#best-practices" >Indexes: best practices</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Troubleshoot
  </div>
  <ul>
<li><a href="/serve-results/troubleshooting/" >Troubleshooting</a></li>
<li><a href="/transform-data/freshness/troubleshoot-freshness/" >Freshness troubleshooting</a></li>
<li><a href="/transform-data/dataflow-troubleshooting/" >Dataflow troubleshooting</a></li>
<li><a href="/transform-data/faq/" >FAQ: Indexes</a></li>
</ul>

</div>

</div>

## Pages in this section

- [Dataflow troubleshooting](/transform-data/dataflow-troubleshooting/index.md): How to troubleshoot common dataflow-level scenarios where Materialize is not working as expected.
- [Dictionary compression](/transform-data/dictionary-compression/index.md): Reduce arrangement memory for columns that hold a small set of repeated values.
- [FAQ: Indexes](/transform-data/faq/index.md): Frequently asked questions about indexes.
- [Freshness](/transform-data/freshness/index.md): Guides for tuning, monitoring, and troubleshooting data freshness in Materialize.
- [Idiomatic Materialize SQL](/transform-data/idiomatic-materialize-sql/index.md): Learn about idiomatic Materialize SQL. Materialize offers various idiomatic query patterns, such as for top-k query pattern, first value/last value query paterrns, etc.
- [Optimization](/transform-data/optimization/index.md): Recommendations for query optimization in Materialize.
- [Patterns](/transform-data/patterns/index.md): Learn about common Materialize query patterns.
- [Updating materialized views](/transform-data/updating-materialized-views/index.md): Strategies for updating materialized views in production.
