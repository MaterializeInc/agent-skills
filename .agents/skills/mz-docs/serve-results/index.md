# Serve results

Serving results from Materialize

In Materialize, indexed views and materialized views maintain up-to-date query
results. This allows Materialize to serve fresh query results with low latency.

To serve results, you can:

- [Query using `SELECT` and `SUBSCRIBE`
  statements](/serve-results/query-results/)

- [Understand the query lifecycle](/serve-results/query-lifecycle/)

- [Use BI/data collaboration tools](/serve-results/bi-tools/)

- [Sink results to external systems](/export-data/)

- [Use Foreign Data Wrapper (FDW)](/serve-results/fdw/)

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    SELECT/SUBSCRIBE statements
  </div>
  <ul>
<li><a href="/serve-results/query-results/" >Query using <code>SELECT</code> and <code>SUBSCRIBE</code></a></li>
<li><a href="/serve-results/query-lifecycle/" >Query lifecycle</a></li>
<li><a href="/serve-results/fdw/" >Use Foreign Data Wrapper (FDW)</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    External BI tools
  </div>
  <ul>
<li><a href="/serve-results/bi-tools/deepnote/" >Deepnote</a></li>
<li><a href="/serve-results/bi-tools/excel/" >Excel</a></li>
<li><a href="/serve-results/bi-tools/hex/" >Hex</a></li>
<li><a href="/serve-results/bi-tools/metabase/" >Metabase</a></li>
<li><a href="/serve-results/bi-tools/power-bi/" >Power BI</a></li>
<li><a href="/serve-results/bi-tools/tableau/" >Tableau</a></li>
<li><a href="/serve-results/bi-tools/looker/" >Looker</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Sink results
  </div>
  <ul>
<li><a href="/export-data/s3/" >Sinking results to Amazon S3</a></li>
<li><a href="/export-data/census/" >Sinking results to Census</a></li>
<li><a href="/export-data/kafka/" >Sinking results to Kafka</a></li>
<li><a href="/export-data/snowflake/" >Sinking results to Snowflake</a></li>
</ul>

</div>

</div>

## Pages in this section

- [`SELECT` and `SUBSCRIBE`](/serve-results/query-results/index.md): Querying results from Materialize using `SELECT` and `SUBSCRIBE`.
- [ADBC (Arrow Database Connectivity)](/serve-results/adbc/index.md): Use the ADBC PostgreSQL driver to pull Materialize results into Apache Arrow
- [Client libraries](/serve-results/client-libraries/index.md): Connect via client libraries/SQL drivers
- [Connect to Materialize via HTTP](/serve-results/http-api/index.md): How to use Materialize via HTTP
- [Connect to Materialize via WebSocket](/serve-results/websocket-api/index.md): How to use Materialize via WebSocket
- [Connection Pooling](/serve-results/connection-pooling/index.md): How to use connection pooling with Materialize
- [Durable subscriptions](/serve-results/durable-subscriptions/index.md): How to enable lossless, durable subscriptions to your changing results in Materialize
- [Foreign data wrapper (FDW) ](/serve-results/fdw-setup/index.md): Use FDW to access Materialize
- [Isolation levels](/serve-results/isolation-level/index.md): Materialize supports different isolation levels that determine how it isolates the execution of transactions.
- [SQL clients](/serve-results/sql-clients/index.md): How to connect to Materialize using common SQL clients
- [Troubleshooting](/serve-results/troubleshooting/index.md): Troubleshooting guides for queries that are slow, unresponsive, or expensive in Materialize.
- [Understand the query lifecycle](/serve-results/query-lifecycle/index.md): Understand how Materialize executes a `SELECT` query, and what latency to expect for each type of query.
- [Use BI/data collaboration tools](/serve-results/bi-tools/index.md): Querying results from Materialize using external BI/data collaboration tools
- [Use foreign data wrapper (FDW)](/serve-results/fdw/index.md): Use FDW to query results from Materialize
