# What is Materialize?

Learn more about Materialize

Materialize is the live data layer for apps and AI agents. To keep results
up-to-date as new data arrives, Materialize incrementally updates results as it
ingests data rather than recalculating results from scratch.

## Materialize offerings

Materialize is available as:

| Offering | Description | Get Started 🚀  |
|----------|-------------|-----------------|
| **Materialize Cloud** | Materialize Cloud is a fully-managed service for Materialize. | Sign up for a [free trial account](https://materialize.com/register/?utm_campaign=General&utm_source=documentation) on Materialize Cloud and try out the [Quickstart](/get-started/quickstart/). |
| **Materialize Self-Managed** | Deploy and operate Materialize in your Kubernetes environment. Whereas Materialize Cloud gives you a fully managed service, Materialize Self-Managed allows you to deploy Materialize in your own infrastructure.<br><br><p>Self-managed Materialize is available as a paid Enterprise Edition and a free
Community Edition:</p>
<table>
  <thead>
      <tr>
          <th>Feature</th>
          <th>Enterprise Edition</th>
          <th>Community Edition</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td><strong>Maximum Usage Limits (Memory)</strong></td>
          <td>None</td>
          <td>24 GiB</td>
      </tr>
      <tr>
          <td><strong>Maximum Usage Limits (Disk)</strong></td>
          <td>None</td>
          <td>48 GiB</td>
      </tr>
      <tr>
          <td><strong><a href="/support/" >Support</a></strong></td>
          <td><a href="https://materialize.com/self-managed/enterprise-license/" >Per terms of your license</a></td>
          <td><a href="/support/" >Community slack or support chat</a></td>
      </tr>
      <tr>
          <td><strong>License</strong></td>
          <td><a href="https://materialize.com/self-managed/enterprise-license/" >Enterprise License - Contact Us</a></td>
          <td><a href="/license/" >BSL/Privacy Policy</a></td>
      </tr>
  </tbody>
</table> | [Install self-managed](/self-managed-deployments/installation/install/) and try out the [Quickstart](/get-started/quickstart/). |
| **Materialize Emulator** | Materialize Emulator is an all-in-one Docker image that provides the fastest way to get hands-on experience with Materialize for local development. | [Download and run Materialize Emulator](/developer-tools/install-materialize-emulator/) and try out the [Quickstart](/get-started/quickstart/). |

## Key features

Materialize combines the accessibility of SQL databases with a streaming engine
that is horizontally scalable, highly available, and strongly consistent.

### Incremental updates

In traditional databases, materialized views help you avoid re-running heavy
queries, typically by caching queries to serve results faster. But you have
to make a compromise between the freshness of the results, the cost of
refreshing the view, and the complexity of the SQL statements you can use.

In Materialize, you don't have to make such compromises. Materialize supports
incrementally updated view results that are **always fresh** (even when using
complex SQL statements, like multi-way joins with aggregations) for *both*:

- [Indexed views](/fundamentals/concepts/views/#indexes-on-views) and

- [Materialized views](/fundamentals/concepts/views/#materialized-views).

How?
Its engine is built on [Timely](https://github.com/TimelyDataflow/timely-dataflow#timely-dataflow)
and [Differential Dataflow](https://github.com/timelydataflow/differential-dataflow#differential-dataflow)
— data processing frameworks backed by many years of research and optimized for
this exact purpose.

### Standard SQL support

With Materialize, you use SQL to transform your fast-changing data into **live
data products**: the business objects (e.g., a customer, an order, a store) that
your applications, services, dashboards, and AI agents read.

You can express complex transformations using **[any type of
join](/sql/select/join/)** (including non-windowed joins and joins on arbitrary
conditions), as well as SQL patterns
enabled by streaming like [**Change Data Capture (CDC)**](/ingest-data/),
[**temporal filters**](/sql/patterns/temporal-filters/), and
[**subscriptions**](/sql/subscribe/).

Materialize follows the SQL standard (SQL-92) implementation and aims for
compatibility with the PostgreSQL dialect. It **does not** aim for
compatibility with a specific version of PostgreSQL. This means that
Materialize might support syntax from any released PostgreSQL version, but does
not provide full coverage of the PostgreSQL dialect. The implementation and
performance of specific features (like [window functions](/transform-data/idiomatic-materialize-sql/appendix/window-function-to-materialize))
might also differ, because Materialize uses an entirely different database
engine based on [Timely and Differential Dataflow](/fundamentals/#incremental-updates).

If you need specific syntax or features that are not currently supported in
Materialize, please submit a [feature request](/support/#share-your-feedback).

### Real-time data ingestion

Materialize supports ingesting data from various external systems:

| Type | External system |
|------|-----------------|
| **Databases (CDC): native connectors** | [PostgreSQL](/ingest-data/postgres/) <br> [MySQL](/ingest-data/mysql/) <br> [SQL Server](/ingest-data/sql-server/) |
| **Databases (CDC): via the Kafka connector** | [CockroachDB](/ingest-data/cdc-cockroachdb/) (using changefeeds) <br> [MongoDB](/ingest-data/mongodb/) (using Debezium) |
| **Message brokers** | [Kafka](/ingest-data/kafka/) <br> [Redpanda](/sql/create-source/kafka) |
| **Webhooks** | [Amazon EventBridge](/ingest-data/webhooks/amazon-eventbridge/) <br> [Segment](/ingest-data/webhooks/segment/) <br> [HubSpot](/ingest-data/webhooks/hubspot/) <br> [RudderStack](/ingest-data/webhooks/rudderstack/) <br> [SnowcatCloud](/ingest-data/webhooks/snowcatcloud/) <br> [Stripe](/ingest-data/webhooks/stripe/)|

For more information, see [Ingest Data](/ingest-data/).

### PostgreSQL wire-compatibility

Every database needs a protocol to standardize communication with the outside
world. Materialize uses the [PostgreSQL wire protocol](https://datastation.multiprocess.io/blog/2022-02-08-the-world-of-postgresql-wire-compatibility.html),
which allows it to integrate out-of-the-box with many SQL clients and other
tools in the data ecosystem that support PostgreSQL — like [dbt](/integrations/dbt/).

### Strong consistency guarantees

By default, Materialize provides the highest level of transaction isolation:
**strict serializability**. This means that it presents as if it were a single
process, despite spanning a large number of threads, processes, and machines.
Strict serializability avoids common pitfalls like eventual consistency and dual
writes, which affect the correctness of your results. You can [adjust the
transaction isolation level](/overview/isolation-level/) depending on your
consistency and performance requirements.

## Learn more

- [Key concepts](/fundamentals/concepts/)
- [Get started with Materialize](/get-started/quickstart)

---

## Architecture Patterns

Pattern | Description
--------|------------
[Live Context Graph](/fundamentals/architecture-patterns/live-context-graph/) | Model your business as a compounding ontology of live data products and build apps, services, and AI agents on top of it.

---

## Concepts

The pages in this section introduces some of the key concepts in Materialize:

Concept                                  | Description
-----------------------------------------|-----
[Clusters](/fundamentals/concepts/clusters/)          | Clusters are isolated pools of compute resources for sources, sinks, indexes, materialized views, and ad-hoc queries.
[Sources](/fundamentals/concepts/sources/)            | Sources describe an external system you want Materialize to read data from.
[Views](/fundamentals/concepts/views/)    | Views represent a named query that you want to save for repeated execution. You can use **indexed views** and **materialized views** to incrementally maintain the results of views.
[Indexes](/fundamentals/concepts/indexes/)            | Indexes represent query results stored in memory.
[Arrangements](/fundamentals/concepts/arrangements/) | Arrangements are the in-memory data structures that maintain indexes and materialized views.
[Sinks](/fundamentals/concepts/sinks/)                | Sinks describe an external system you want Materialize to write data to.
[Snapshotting](/fundamentals/concepts/snapshotting/) | The initial sync of a source's data from an upstream system, before the source can serve queries.
[Hydration](/fundamentals/concepts/hydration/) | Hydration is the reconstruction of an object's in-memory state by reading
from Materialize's storage layer and existing indexes; hydration does not
read from the upstream system.

[Reaction Time](/fundamentals/concepts/reaction-time) | Measures how quickly a system can reflect a change in input data and return an up-to-date query result. Defined as the sum of data freshness and query latency.

Refer to the individual pages for more information.

