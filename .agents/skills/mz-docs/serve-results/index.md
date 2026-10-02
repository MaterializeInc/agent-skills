# Serve results

Serving results from Materialize

In Materialize, indexed views and materialized views maintain up-to-date query
results. This allows Materialize to serve fresh query results with low latency.

To serve results, you can:

- [Query using `SELECT` and `SUBSCRIBE`
  statements](/serve-results/query-results/)

- [Use BI/data collaboration tools](/serve-results/bi-tools/)

- [Sink results to to external systems](/export-data/)

- [Use Foreign Data Wrapper (FDW)](/serve-results/fdw/)

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    SELECT/SUBSCRIBE statements
  </div>
  <ul>
<li><a href="/serve-results/query-results/" >Query using <code>SELECT</code> and <code>SUBSCRIBE</code></a></li>
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

---

## `SELECT` and `SUBSCRIBE`

You can query results from Materialize using `SELECT` and `SUBSCRIBE` SQL
statements. Because Materialize uses the PostgreSQL wire protocol, it works
out-of-the-box with a wide range of SQL clients and tools that support
PostgreSQL.

## SELECT

You can query data in Materialize using the [`SELECT` statement](/sql/select/).
For example:

```mzsql
SELECT region.id, sum(purchase.total)
FROM mysql_simple_purchase AS purchase
JOIN mysql_simple_user AS user ON purchase.user_id = user.id
JOIN mysql_simple_region AS region ON user.region_id = region.id
GROUP BY region.id;
```

Performing a `SELECT` on an indexed view or an indexed materialized view is
Materialize's ideal operation. When Materialize receives such a `SELECT` query,
it quickly returns the maintained results from memory.

Materialize also quickly returns results for queries that only filter, project,
transform with scalar functions, and re-order data that is maintained by an
index.

Queries that can't simply read out from an index will create an ephemeral dataflow to compute
the results. These dataflows are bound to the active [cluster](/fundamentals/concepts/clusters/),
 which you can change using:

```mzsql
SET cluster = <cluster name>;
```

Materialize will remove the dataflow as soon as it has returned the query
results to you.

For more information, see [`SELECT`](/sql/select/) reference page.  See
also the following client library guides:

<ul style="column-count: 2"><li><a href="/serve-results/client-libraries/golang/#query" >Go</a></li></li><li><a href="/serve-results/client-libraries/java-jdbc/#query" >Java</a></li></li><li><a href="/serve-results/client-libraries/node-js/#query" >Node.js</a></li></li><li><a href="/serve-results/client-libraries/php/#query" >PHP</a></li></li><li><a href="/serve-results/client-libraries/python/#query" >Python</a></li></li><li><a href="/serve-results/client-libraries/ruby/#query" >Ruby</a></li></li><li><a href="/serve-results/client-libraries/rust/#query" >Rust</a></li></li></ul>

## SUBSCRIBE

You can use [`SUBSCRIBE`](/sql/subscribe/) to stream query results.  For
example:

```mzsql
BEGIN;
DECLARE c CURSOR FOR SUBSCRIBE (SELECT * FROM mv_counter_sum);
FETCH 10 c WITH (timeout='1s');
FETCH 20 c WITH (timeout='1s');
COMMIT;
```

The [`SUBSCRIBE`](/sql/subscribe/) statement is a more general form of a `SELECT` statement. While a `SELECT` statement computes a relation at a moment in time, a `SUBSCRIBE` operation computes how a relation changes over time.

You can use `SUBSCRIBE` to:

- Power event processors that react to every change to a relation or an
  arbitrary `SELECT` statement.

- Replicate the complete history of a relation while `SUBSCRIBE` is active.

> **Tip:** Use materialized view (instead of an indexed view) with `SUBSCRIBE`.

For more information, see [`SUBSCRIBE`](/sql/subscribe/) reference page.  See
also the following client library guides:

<ul style="column-count: 2"><li><a href="/serve-results/client-libraries/golang/#stream" >Go</a></li></li><li><a href="/serve-results/client-libraries/java-jdbc/#stream" >Java</a></li></li><li><a href="/serve-results/client-libraries/node-js/#stream" >Node.js</a></li></li><li><a href="/serve-results/client-libraries/php/#stream" >PHP</a></li></li><li><a href="/serve-results/client-libraries/python/#stream" >Python</a></li></li><li><a href="/serve-results/client-libraries/ruby/#stream" >Ruby</a></li></li><li><a href="/serve-results/client-libraries/rust/#stream" >Rust</a></li></li></ul>

---

## ADBC (Arrow Database Connectivity)

[ADBC (Arrow Database Connectivity)](https://arrow.apache.org/adbc/) is a
standard, columnar database API from Apache Arrow. Because Materialize is
**wire-compatible** with PostgreSQL, the community [ADBC PostgreSQL
driver](https://arrow.apache.org/adbc/current/driver/postgresql.html)
(`adbc_driver_postgresql`) can connect directly to Materialize; i.e., no
Materialize-specific driver is required.

The benefit over a standard PostgreSQL client is the result format. ADBC returns
query results as [Apache Arrow](https://arrow.apache.org/) tables, which you can
hand directly to Arrow-native tools such as [DuckDB](https://duckdb.org/),
[pandas](https://pandas.pydata.org/), and [Polars](https://pola.rs/) without an
intermediate object-store or file hop.

## Prerequisites

Requires **Materialize v26.40 or later**. When it opens a connection, the driver
reads the binary send and receive functions of every type from
`pg_catalog.pg_type`. Earlier versions of Materialize do not expose
`pg_type.typsend`, so `connect()` fails before it can run a query.

Install the driver manager, the PostgreSQL driver, and PyArrow. The examples on
this page also use DuckDB:

```bash
pip install adbc-driver-manager adbc-driver-postgresql pyarrow duckdb
```

The examples were tested with `adbc-driver-manager` and
`adbc-driver-postgresql` 1.12.0, `pyarrow` 25.0.1, and `duckdb` 1.5.5.

## Connect

Connect using `adbc_driver_postgresql.dbapi.connect` with a PostgreSQL
connection URI. Use the connection as a context manager so that it closes when
the block exits:

```python
import adbc_driver_postgresql.dbapi
from urllib.parse import quote_plus

username = quote_plus("MATERIALIZE_USERNAME")
password = quote_plus("APP_SPECIFIC_PASSWORD")

uri = (
    f"postgresql://{username}:{password}"
    "@MATERIALIZE_HOST:6875/materialize?sslmode=require"
)

with adbc_driver_postgresql.dbapi.connect(uri) as conn:
    # Run queries here.
    ...
```

> **Tip:** Percent-encode the username and password before putting them in the URI, as in
> the example above. Materialize usernames are email addresses, so they contain an
> `@`, which delimits the host in a URI. App passwords can likewise contain
> characters that a URI reserves.

> **Note:** `sslmode=require` applies to Materialize Cloud, which accepts only TLS
> connections. A self-managed deployment accepts TLS only if you have configured
> it to serve TLS, so set `sslmode` to match your deployment.

For where to find your host name, database, and app password, see [SQL
clients](/serve-results/sql-clients/).

## Query and fetch as Arrow

Execute a query with a cursor, then call `fetch_arrow_table` to get a
[`pyarrow.Table`](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html):

```python
with adbc_driver_postgresql.dbapi.connect(uri) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT n, n * 2 AS doubled FROM generate_series(1, 100) AS g(n)")
        table = cur.fetch_arrow_table()

print(table.schema)
print(table.num_rows)
```

```nofmt
n: int32
doubled: int32
100
```

The Arrow table holds the full result in memory, so it stays usable after the
connection closes.

## Hand off to DuckDB

Because the result is already an Arrow table, an Arrow-native engine can read it
in place. DuckDB queries the `table` from the previous section directly, with no
S3 or file hop:

```python
import duckdb

con = duckdb.connect()
con.register("t", table)
print(con.execute("SELECT sum(doubled) FROM t WHERE n > 50").fetchall())
```

```nofmt
[(7550,)]
```

The same pattern works for any Arrow consumer. For example,
`table.to_pandas()` produces a pandas DataFrame, and
`polars.from_arrow(table)` produces a Polars DataFrame.

## Type mapping

The driver maps the types Materialize shares with PostgreSQL to Arrow types as
follows:

Materialize / PostgreSQL type | Arrow type
----------------------------- | ----------
`bool`                        | `bool`
`int2` (`smallint`)           | `int16`
`int4` (`integer`)            | `int32`
`int8` (`bigint`)             | `int64`
`float4` (`real`)             | `float32`
`float8` (`double precision`) | `float64`
`text`, `varchar`             | `string`
`bytea`                       | `binary`
`date`                        | `date32`
`time`                        | `time64` (microseconds)
`timestamp`                   | `timestamp` (microseconds)
`timestamptz`                 | `timestamp` (microseconds, UTC)
`interval`                    | `month_day_nano_interval`
`jsonb`                       | `json` (over `string`)
`numeric`                     | `opaque` extension (over `string`)
`uuid`                        | `opaque` extension (over `binary`)
arrays (for example `int4[]`) | `list` of the element type

> **Note:** `numeric` and `uuid` have no native Arrow type, so the driver wraps them in an
> [Arrow `opaque` extension
> type](https://arrow.apache.org/docs/format/CanonicalExtensions.html#opaque)
> over `string` and `binary` storage respectively.

The driver picks the Arrow type for a column from the name of that type's
PostgreSQL binary receive function. Materialize-specific types
([`list`](/sql/types/list/), [`map`](/sql/types/map/),
[`uint2`/`uint4`/`uint8`](/sql/types/uint/), `mz_timestamp`, and `mz_aclitem`)
have no PostgreSQL receive function. Rather than erroring, the driver falls back
to an `opaque` extension type over binary for them, which holds the raw binary
`COPY` encoding of the value. To get a usable Arrow value for one of these
types, cast it in the query, for example `my_list::text`.

The driver retrieves results using PostgreSQL's binary `COPY` protocol.

## Learn more

- [SQL clients](/serve-results/sql-clients/) for connection parameters and app
  passwords.
- [Client libraries](/serve-results/client-libraries/) for other language
  clients.
- [Apache Arrow ADBC documentation](https://arrow.apache.org/adbc/) for the ADBC
  API and driver details.

---

## Client libraries

Applications can use various common language-specific PostgreSQL client
libraries to interact with Materialize and **create relations**, **execute
queries** and **stream out results**.

> **Note:** Client libraries tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if PostgreSQL is supported, it's **not guaranteed** that the same integration will work out-of-the-box.

| Language | Tested drivers                                                  | Notes                                                 |
| -------- | --------------------------------------------------------------- | ----------------------------------------------------- |
| Go       | [`pgx`](https://github.com/jackc/pgx)                           | See the [Go cheatsheet](/serve-results/client-libraries/golang/).       |
| Java     | [PostgreSQL JDBC driver](https://jdbc.postgresql.org/)          | See the [Java cheatsheet](/serve-results/client-libraries/java-jdbc/).  |
| Node.js  | [`node-postgres`](https://node-postgres.com/)                   | See the [Node.js cheatsheet](/serve-results/client-libraries/node-js/). |
| PHP      | [`pdo_pgsql`](https://www.php.net/manual/en/ref.pgsql.php)      | See the [PHP cheatsheet](/serve-results/client-libraries/php/).         |
| Python   | [`psycopg2`](https://pypi.org/project/psycopg2/)                | See the [Python cheatsheet](/serve-results/client-libraries/python/) and its [SQLAlchemy section](/serve-results/client-libraries/python/#sqlalchemy). |
| Ruby     | [`pg` gem](https://rubygems.org/gems/pg/)                       | See the [Ruby cheatsheet](/serve-results/client-libraries/ruby/).       |
| Rust     | [`postgres-openssl`](https://crates.io/crates/postgres-openssl) | See the [Rust cheatsheet](/serve-results/client-libraries/rust/).       |

👋 _Is there another client library you'd like to use with Materialize? Submit a
[feature
request](https://github.com/MaterializeInc/materialize/discussions/new?category=feature-requests&labels=A-integration)._

---

## Connect to Materialize via HTTP

You can access Materialize through its "session-less" HTTP API endpoint:

```bash
https://<MZ host address>/api/sql
```

## Details

### General semantics

The API:

- Requires username/password authentication, just as connecting via a SQL
  client (e.g. `psql`). Materialize provides you the username and password upon
  setting up your account.
- Requires that you provide the entirety of your request. The API does not
  provide session-like semantics, so there is no way to e.g. interactively use
  transactions.
- Ceases to process requests upon encountering the first error.
- Does not support statements whose semantics rely on sessions or whose state is
  indeterminate at the end of processing, including:
    - `CLOSE`
    - `COPY`
    - `DECLARE`
    - `FETCH`
    - `SUBSCRIBE`
- Supports specifying run-time [configuration parameters](/sql/set)
  via URL query parameters.

### Transactional semantics

The HTTP API provides two modes with slightly different transactional semantics from one another:

- **Simple**, which mirrors PostgreSQL's [Simple Query][simple-query] protocol.
    - Supports a single query, but the single query string may contain multiple
      statements, e.g. `SELECT 1; SELECT 2;`
    - Treats all statements as in an implicit transaction unless other
      transaction control is invoked.
- **Extended**, which mirrors PostgreSQL's [Extended Query][extended-query] protocol.
    - Supports multiple queries, but only one statement per query string.
    - Supports parameters.
    - Eagerly commits DDL (e.g. `CREATE TABLE`) in implicit transactions, but
      not DML (e.g. `INSERT`).

### OpenAPI spec

Download our [OpenAPI](https://swagger.io/specification/) v3 spec for this
interface: [environmentd-openapi.yml](/materialize-openapi.yml).

## Usage

### Endpoint

```
https://<MZ host address>/api/sql
```

Accessing the endpoint requires [basic authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme). Reuse the same credentials as with a SQL client (e.g. `psql`):

* **User ID:** Your email to access Materialize.
* **Password:** Your app password.

#### Query parameters

You can optionally specify configuration parameters for each request, as a URL-encoded JSON object, with the `options` query parameter:

```
https://<MZ host address>/api/sql?options=<object>
```

For example, this is how you could specify the `application_name` configuration parameter with JavaScript:

```javascript
// Create and encode our parameters object.
const options = { application_name: "my_app" };
const encoded = encodeURIComponent(JSON.stringify(options));

// Add the object to our URL as the "options" query parameter.
const url = new URL(`https://${mzHostAddress}/api/sql`);
url.searchParams.append("options", encoded);
```

### Input format

#### Simple

The request body is a JSON object containing a key, `query`, which specifies the
SQL string to execute. `query` may contain multiple SQL statements separated by
semicolons.

```json
{
    "query": "select * from a; select * from b;"
}
```

#### Extended

The request body is a JSON object containing a key `queries`, whose value is
array of objects, whose structure is:

Key | Value
----|------
`query` | A SQL string containing one statement to execute
`params` | An optional array of text values to be used as the parameters to `query`. _null_ values are converted to _null_ values in Materialize. Note that all parameter values' elements must be text or _null_; the API will not accept JSON numbers.

```json
{
    "queries": [
        { "query": "select * from a;" },
        { "query": "select a + $1 from a;", "params": ["100"] }
        { "query": "select a + $1 from a;", "params": [null] }
    ]
}
```

### Output format

The output format is a JSON object with one key, `results`, whose value is
an array of the following:

Result | JSON value
---------------------|------------
Rows | `{"rows": <2D array of JSON-ified results>, "desc": <array of column descriptions>, "notices": <array of notices>}`
Error | `{"error": <Error object from execution>, "notices": <array of notices>}`
Ok | `{"ok": <tag>, "notices": <array of notices>}`

Each committed statement returns exactly one of these values; e.g. in the case
of "complex responses", such as `INSERT INTO...RETURNING`, the presence of a
`"rows"` object implies `"ok"`.

The `"notices"` array is present in all types of results and contains any
diagnostic messages that were generated during execution of the query. It has
the following structure:

```
{"severity": <"warning"|"notice"|"debug"|"info"|"log">, "message": <informational message>}
```

Note that the returned values include the results of statements which were
ultimately rolled back because of an error in a later part of the transaction.
You must parse the results to understand which statements ultimately reflect
the resultant state.

Numeric results are converted to strings to avoid possible JavaScript number inaccuracy.
Column descriptions contain the name, oid, data type size and type modifier of a returned column.

#### TypeScript definition

You can model these with the following TypeScript definitions:

```typescript
interface Simple {
    query: string;
}

interface ExtendedRequest {
    query: string;
    params?: (string | null)[];
}

interface Extended {
    queries: ExtendedRequest[];
}

type SqlRequest = Simple | Extended;

interface Notice {
	message: string;
	severity: string;
	detail?: string;
	hint?: string;
}

interface Error {
	message: string;
	code: string;
	detail?: string;
	hint?: string;
}

interface Column {
    name: string;
    type_oid: number; // u32
    type_len: number; // i16
    type_mod: number; // i32
}

interface Description {
	columns: Column[];
}

type SqlResult =
  | {
	tag: string;
	rows: any[][];
	desc: Description;
	notices: Notice[];
} | {
	ok: string;
	notices: Notice[];
} | {
	error: Error;
	notices: Notice[];
};
```

## Examples
### Run a transaction

Use the [extended input format](#extended) to run a transaction:
```bash
curl 'https://<MZ host address>/api/sql' \
    --header 'Content-Type: application/json' \
    --user '<username>:<passsword>' \
    --data '{
        "queries": [
            { "query": "CREATE TABLE IF NOT EXISTS t (a int);" },
            { "query": "CREATE TABLE IF NOT EXISTS s (a int);" },
            { "query": "BEGIN;" },
            { "query": "INSERT INTO t VALUES ($1), ($2)", "params": ["100", "200"] },
            { "query": "COMMIT;" },
            { "query": "BEGIN;" },
            { "query": "INSERT INTO s VALUES ($1), ($2)", "params": ["9", null] },
            { "query": "COMMIT;" }
        ]
    }'
```

Response:
```json
{
  "results": [
    {"ok": "CREATE TABLE", "notices": []},
    {"ok": "CREATE TABLE", "notices": []},
    {"ok": "BEGIN", "notices": []},
    {"ok": "INSERT 0 2", "notices": []},
    {"ok": "COMMIT", "notices": []},
    {"ok": "BEGIN", "notices": []},
    {"ok": "INSERT 0 2", "notices": []},
    {"ok": "COMMIT", "notices": []}
  ]
}
```

### Run a query

Use the [simple input format](#simple) to run a query:
```bash
curl 'https://<MZ host address>/api/sql' \
    --header 'Content-Type: application/json' \
    --user '<username>:<passsword>' \
    --data '{
        "query": "SELECT t.a + s.a AS cross_add FROM t CROSS JOIN s; SELECT a FROM t WHERE a IS NOT NULL;"
    }'
```

Response:
```json
{
  "results": [
    {
      "desc": {
        "columns": [
          {
            "name": "cross_add",
            "type_len": 4,
            "type_mod": -1,
            "type_oid": 23
          }
        ]
      },
      "notices": [],
      "rows": [],
      "tag": "SELECT 0"
    },
    {
      "desc": {
        "columns": [
          {
            "name": "a",
            "type_len": 4,
            "type_mod": -1,
            "type_oid": 23
          }
        ]
      },
      "notices": [],
      "rows": [],
      "tag": "SELECT 0"
    }
  ]
}
```

## See also
- [SQL Clients](../sql-clients)

[simple-query]: https://www.postgresql.org/docs/current/protocol-flow.html#id-1.10.5.7.4
[extended-query]: https://www.postgresql.org/docs/current/protocol-flow.html#PROTOCOL-FLOW-EXT-QUERY

---

## Connect to Materialize via WebSocket

You can access Materialize through its interactive WebSocket API endpoint:

```bash
wss://<MZ host address>/api/experimental/sql
```

## Details

### General semantics

The API:

- Requires username/password authentication, just as connecting via a SQL
  client (e.g. `psql`). Materialize provides you the username and password upon
  setting up your account.
- Maintains an interactive session.
- Does not support some statements:
    - `CLOSE`
    - `COPY`
    - `DECLARE`
    - `FETCH`
- Supports specifying run-time configuration parameters ([session variables](https://www.postgresql.org/docs/current/sql-set.html))
  via the initial authentication message.

### Transactional semantics

The WebSocket API provides two modes with slightly different transactional semantics from one another:

- **Simple**, which mirrors PostgreSQL's [Simple Query][simple-query] protocol.
    - Supports a single query, but the single query string may contain multiple
      statements, e.g. `SELECT 1; SELECT 2;`
    - Treats all statements as in an implicit transaction unless other
      transaction control is invoked.
- **Extended**, which mirrors PostgreSQL's [Extended Query][extended-query] protocol.
    - Supports multiple queries, but only one statement per query string.
    - Supports parameters.
    - Eagerly commits DDL (e.g. `CREATE TABLE`) in implicit transactions, but
      not DML (e.g. `INSERT`).

## Usage

### Endpoint

```
wss://<MZ host address>/api/experimental/sql
```

To authenticate using a username and password, send an initial text or binary message containing a JSON object:

```
{
    "user": "<Your email to access Materialize>",
    "password": "<Your app password>",
    "options": { <Optional map of session variables> }
}
```

To authenticate using a token, send an initial text or binary message containing a JSON object:

```
{
    "token": "<Your access token>",
    "options": { <Optional map of session variables> }
}
```

Successful authentication will result in:

- Some `ParameterStatus` messages indicating the values of some initial session settings.
- One `BackendKeyData` message that can be used for cancellation.
- One `ReadyForQuery`message, at which point the server is ready to receive requests.

An error during authentication is indicated by a websocket Close message.
HTTP `Authorization` headers are ignored.

### Messages

WebSocket Text or Binary messages can be sent.
The payload is described below in the [Input format](#input-format) section.
Each request will respond with some number of response messages, followed by a `ReadyForQuery` message.
There is exactly one `ReadyForQuery` message for each request, regardless of how many queries the request contains.

### Input format

#### Simple

The message payload is a JSON object containing a key, `query`, which specifies the
SQL string to execute. `query` may contain multiple SQL statements separated by
semicolons.

```json
{
    "query": "select * from a; select * from b;"
}
```

#### Extended

The message payload is a JSON object containing a key `queries`, whose value is
array of objects, whose structure is:

Key | Value
----|------
`query` | A SQL string containing one statement to execute
`params` | An optional array of text values to be used as the parameters to `query`. _null_ values are converted to _null_ values in Materialize. Note that all parameter values' elements must be text or _null_; the API will not accept JSON numbers.

```json
{
    "queries": [
        { "query": "select * from a;" },
        { "query": "select a + $1 from a;", "params": ["100"] }
        { "query": "select a + $1 from a;", "params": [null] }
    ]
}
```

### Output format

The response messages are WebSocket Text messages containing a JSON object that contains keys `type` and `payload`.

`type` value | Description
---------------------|------------
`ReadyForQuery` | Sent at the end of each response batch
`Notice` | An informational notice.
`CommandStarting` | A command has executed and response data will be returned.
`CommandComplete` | Executing a statement succeeded.
`Error` | Executing a statement resulted in an error.
`Rows` | A rows-returning statement is executing, and some `Row` messages may follow.
`Row` | A single row result.
`ParameterStatus` | Announces the value of a session setting.
`BackendKeyData` | Information used to cancel queries.

#### `ReadyForQuery`

Exactly one of these is sent at the end of every request batch.
It can be used to synchronize with the server, and means the server is ready for another request.
(However, many requests can be made at any time; there is no need to wait for this message before issuing more requests.)
The payload is a `string` describing the current transaction state:

- `I` for idle: not in a transaction.
- `T` for in a transaction.
- `E` for a transaction in an error state. A request starting with `ROLLBACK` should be issued to exit it.

#### `Notice`

A notice can appear at any time and contains diagnostic messages that were generated during execution of the query.
The payload has the following structure:

```
{
    "message": <informational message>,
    "code": <notice code>,
    "severity": <"warning"|"notice"|"debug"|"info"|"log">,
    "detail": <optional error detail>,
    "hint": <optional error hint>,
}
```

#### `Error`

Executing a statement resulted in an error.
The payload has the following structure:

```
{
    "message": <informational message>,
    "code": <error code>,
    "detail": <optional error detail>,
    "hint": <optional error hint>,
}
```

#### `CommandStarting`

A statement has executed and response data will be returned.
This message can be used to know if rows or streaming data will follow.
The payload has the following structure:

```
{
    "has_rows": <boolean>,
    "is_streaming": <boolean>,
}
```

The `has_rows` field is `true` if a `Rows` message will follow.
The `is_streaming` field is `true` if there is no expectation that a `CommandComplete` message will ever occur.
This is the case for `SUBSCRIBE` queries.

#### `CommandComplete`

Executing a statement succeeded.
The payload is a `string` containing the statement's tag.

#### `Rows`

A rows-returning statement is executing and some number (possibly 0) of `Row` messages will follow.
Either a `CommandComplete` or `Error` message will then follow indicating there are no more rows and the final result of the statement.
The payload has the following structure:

```
{
    "columns":
        [
            {
                "name": <column name>,
                "type_oid": <type oid>,
                "type_len": <type len>,
                "type_mod": <type mod>
            }
            ...
        ]
}
```

The inner object's various `type_X` fields are lower-level details that can be used to convert the row results from a string to a more specific data type.
`type_oid` is the OID of the data type.
`type_len` is the data size type (see `pg_type.typlen`).
`type_mod` is the type modifier (see `pg_attribute.atttypmod`).

#### `Row`

A single row result.
Will only occur after a `Rows` message.
The payload is an array of JSON values corresponding to the columns from the `Rows` message.
Numeric results are converted to strings to avoid possible JavaScript number inaccuracy.

#### `ParameterStatus`

Announces the value of a session setting.
These are sent during startup and when a statement caused a session parameter to change.
The payload has the following structure:

```
{
    "name": <name of parameter>,
    "value": <new value of parameter>,
}
```

#### `BackendKeyData`

Information used to cancel queries.
The payload has the following structure:

```
{
    "conn_id": <connection id>,
    "secret_key": <secret key>,
}
```

#### TypeScript definition

You can model these with the following TypeScript definitions:

```typescript
type Auth =
    | { user: string; password: string; options?: { [name: string]: string } }
    | { token: string; options?: { [name: string]: string } }
    ;

interface Simple {
    query: string;
}

interface ExtendedRequest {
    query: string;
    params?: (string | null)[];
}

interface Extended {
    queries: ExtendedRequest[];
}

type SqlRequest = Simple | Extended;

interface Notice {
	message: string;
	severity: string;
	detail?: string;
	hint?: string;
}

interface Error {
	message: string;
	code: string;
	detail?: string;
	hint?: string;
}

interface ParameterStatus {
	name: string;
	value: string;
}

interface CommandStarting {
	has_rows: boolean;
	is_streaming: boolean;
}

interface BackendKeyData {
	conn_id: number; // u32
	secret_key: number; // u32
}

interface Column {
    name: string;
    type_oid: number; // u32
    type_len: number; // i16
    type_mod: number; // i32
}

interface Description {
	columns: Column[];
}

type WebSocketResult =
    | { type: "ReadyForQuery"; payload: string }
    | { type: "Notice"; payload: Notice }
    | { type: "CommandComplete"; payload: string }
    | { type: "Error"; payload: Error }
    | { type: "Rows"; payload: Description }
    | { type: "Row"; payload: any[] }
    | { type: "ParameterStatus"; payload: ParameterStatus }
    | { type: "CommandStarting"; payload: CommandStarting }
    | { type: "BackendKeyData"; payload: BackendKeyData }
    ;
```

## Examples

### Run a query

```bash
$ echo '{"query": "select 1,2; values (4), (5)"}' | websocat wss://<MZ host address>/api/experimental/sql
{"type":"CommandStarting","payload":{"has_rows":true,"is_streaming":false}}
{"type":"Rows","payload":{"columns":[{"name":"?column?","type_oid":23,"type_len":4,"type_mod":-1},{"name":"?column?","type_oid":23,"type_len":4,"type_mod":-1}]}}
{"type":"Row","payload":["1","2"]}
{"type":"CommandComplete","payload":"SELECT 1"}
{"type":"CommandStarting","payload":{"has_rows":true,"is_streaming":false}}
{"type":"Rows","payload":{"columns":[{"name":"column1","type_oid":23,"type_len":4,"type_mod":-1}]}}
{"type":"Row","payload":["4"]}
{"type":"Row","payload":["5"]}
{"type":"CommandComplete","payload":"SELECT 2"}
{"type":"ReadyForQuery","payload":"I"}
```

## See also
- [SQL Clients](../sql-clients)

[simple-query]: https://www.postgresql.org/docs/current/protocol-flow.html#id-1.10.5.7.4
[extended-query]: https://www.postgresql.org/docs/current/protocol-flow.html#PROTOCOL-FLOW-EXT-QUERY

---

## Connection Pooling

Because Materialize is wire-compatible with PostgreSQL, you can use any
PostgreSQL connection pooler with Materialize. In this guide, we’ll cover how to
use connection pooling with Materialize, alongside the common tool PgBouncer.

## PgBouncer
[PgBouncer](https://www.pgbouncer.org/) is a popular connection pooler for
PostgreSQL. It provides a lightweight and efficient way to manage database
connections, reducing the overhead of establishing new connections and
improving performance.

### Step 1: Install PgBouncer

You can [install PgBouncer](https://www.pgbouncer.org/downloads/) on your local machine or on a server.

### Step 2: Create an authentication userlist file

The userlist file contains the credentials for your Materialize user/app. The file has the format of:

```
"user@example.com" "mypassword-or-scram-secret"
```

#### If using `auth_type = plain` (Cloud and Self-Managed)

Specify the password in plaintext:

- **For Cloud**, use the password from an existing [Service Account](https://materialize.com/docs/security/cloud/users-service-accounts/create-service-accounts/) or generate a [new one](https://materialize.com/docs/security/cloud/users-service-accounts/create-service-accounts/).
- **For Self-Managed**, use the password associated with the role.

Example userlist file:
```
"foo@bar.com" "mypassword"
```

#### If using `auth_type = scram-sha-256` (Self-Managed only)

Specify the SCRAM secret. To find the SCRAM secret, run the following query as a superuser:

```sql
SELECT rolname, rolpassword FROM pg_authid WHERE rolname = 'your_role_name';
```

> **Note:** You must be a superuser to access the `pg_authid` table.

Once you have the SCRAM secret, add it to the userlist file in the following format:
```
"your_role_name" "the-hash-you-got-from-pg_authid"
```

### Step 3: Configure PgBouncer to connect to your Materialize instance

1. Locate the configuration file. Refer to the [setup instructions](https://www.pgbouncer.org/downloads/) for your environment.

2. Update the file to:
   - Define a database named `materialize` with your Materialize connection details.
   - Configure PgBouncer as needed for your PgBouncer instance. Be sure to specify the `auth_type` and `auth_file` needed to connect to Materialize.

For example, the following is a basic configuration example to connect a local PgBouncer to a locally-running Materialize:

```ini
[databases]
;; For Cloud, use the connection details from the Console.
;; For Self-Managed, use your Materialize's connection details.
materialize = host=localhost port=6877

[pgbouncer]
logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid
;; Listen on localhost:6432 for incoming connections
listen_addr = localhost
listen_port = 6432

;; Set the authentication type
;; Materialize supports both plain and scram-sha-256.
;; Cloud and Self-Managed support plain.
;; auth_type = plain
;; Self-Managed also supports scram-sha-256:
auth_type = scram-sha-256

;; Set the authentication user list file
auth_file = /etc/pgbouncer/userlist.txt
```

For additional information on configuring PgBouncer, refer to the [PgBouncer documentation](https://www.pgbouncer.org/config.html).

### Step 4: Start the service and connect

After configuring PgBouncer, you can start the service. You can then connect to PgBouncer using the same connection parameters as you would for Materialize, but with the PgBouncer port (default is 6432). For example:

```bash
psql -h localhost -p 6432 -U your_role_name -d materialize
```

---

## Durable subscriptions

[//]: # "TODO: Move to Serve results section"

[Subscriptions](/sql/subscribe/) allow you to stream changing results from
Materialize to an external application programatically. Like any connection over
the network, subscriptions might get disrupted for both expected and unexpected
reasons. In such cases, it can be useful to have a mechanism to gracefully
recover data processing.

To avoid the need for re-processing data that was already sent to your external
application following a connection disruption, you can:

- Adjust the [history retention period](#history-retention-period) for the
  objects that a subscription depends on, and

- [Access past versions of this
  data](#enabling-durable-subscriptions-in-your-application) at specific points
  in time to pick up data processing where you left off.

## History retention period

By default, all user-defined sources, tables, materialized views, and indexes
keep track of the most recent version of their underlying data. To gracefully
recover from connection disruptions and enable lossless, _durable
subscriptions_, you can configure the sources, tables, and materialized views
that the subscription depends on to **retain history**.

> **Important:** Configuring indexes to retain history is not recommended. Instead, consider
> creating a materialized view for your subscription query and configuring the
> history retention period on that view.

To configure the history retention period for sources, tables and materialized
views, use the `RETAIN HISTORY` option in its `CREATE` statement. This value can
also be adjusted at any time using the object-specific `ALTER` statement.

### Semantics

#### Increasing the history retention period

When you increase the history retention period for an object, both the existing
historical data and any subsequently produced historical data are retained for
the specified time period.

**For sources, tables and materialized views:** increasing the history retention
  period will not restore older historical data that was already outside the
  previous history retention period before the change.

Configuring indexes to retain history is not recommended. Instead, consider
creating a materialized view for your subscription query and configuring the
history retention period on that view.

See also [Considerations](#considerations).

#### Decreasing the history retention period

When you decrease the history retention period for an object:

* Newly produced historical data is retained for the new, shorter history
  retention period.

* Historical data outside the new, shorter history retention period is no longer
  retained. If you subsequently increase the history retention period again,
  the older historical data may already be unavailable.

See also [Considerations](#considerations).

### Set history retention period

> **Important:** Setting the history retention period for an object will lead to increased
> resource utilization. Moreover, for indexes, setting history retention period is
> not recommended. Instead, consider creating a materialized view for your
> subscription query and configuring the history retention period on that view.
> See [Considerations](#considerations).

To set the history retention period for [sources](/sql/create-source/),
[tables](/sql/create-table/), and [materialized
views](/sql/create-materialized-view/), you can either:

- Specify the `RETAIN HISTORY` option in the `CREATE` statement. The `RETAIN
   HISTORY` option accepts positive [interval](/sql/types/interval/)
   values (e.g., `'1hr'`). For example:

   ```mzsql
   CREATE MATERIALIZED VIEW winning_bids
   WITH (RETAIN HISTORY FOR '1hr') AS
   SELECT auction_id,
         bid_id,
         item,
         amount
   FROM highest_bid_per_auction
   WHERE end_time < mz_now();
   ```

- Specify the `RETAIN HISTORY` option in the `ALTER` statement. The `RETAIN
  HISTORY` option accepts positive [interval](/sql/types/interval/) values
  (e.g., `'1hr'`). For example:

  ```mzsql
  ALTER MATERIALIZED VIEW winning_bids SET (RETAIN HISTORY FOR '2hr');
  ```

### View history retention period for an object

To see what history retention period has been configured for an object, look up
the object in the
[`mz_internal.mz_history_retention_strategies`](/sql/system-catalog/mz_internal/#mz_history_retention_strategies)
catalog table. For example:

```mzsql
SELECT
    d.name AS database_name,
    s.name AS schema_name,
    mv.name,
    hrs.strategy,
    hrs.value
FROM
    mz_catalog.mz_materialized_views AS mv
        LEFT JOIN mz_schemas AS s ON mv.schema_id = s.id
        LEFT JOIN mz_databases AS d ON s.database_id = d.id
        LEFT JOIN mz_internal.mz_history_retention_strategies AS hrs ON mv.id = hrs.id
WHERE mv.name = 'winning_bids';
```

If set, the returning result includes the value (in milliseconds) of the history
retention period:

```nofmt

 database_name | schema_name |     name     | strategy |  value
---------------+-------------+--------------+----------+---------
 materialize   | public      | winning_bids | FOR      | 7200000
```

### Unset/reset history retention period

To disable history retention, reset the history retention period; i.e., specify
the `RESET (RETAIN HISTORY)` option in the `ALTER` statement. For example:

```mzsql
ALTER MATERIALIZED VIEW winning_bids RESET (RETAIN HISTORY);
```

### Considerations

#### Resource utilization

Increasing the history retention period for an object will lead to increased
resource utilization in Materialize.

**For sources, tables and materialized views:**  Increasing the history
retention period for these objects increases the amount of historical data that
is retained in the storage layer. You can expect storage resource utilization to
increase, which may incur additional costs.

**For indexes:** Configuring indexes to retain history is not recommended.
Instead, consider creating a materialized view for your subscription query and
configuring the history retention period on that view.

#### Best practices

- Because of the increased storage costs and processing time for the additional
  historical data, consider configuring history retention period on the object
  directly powering the subscription, rather than all the way through the
  dependency chain from the source to the materialized view.

- Configuring indexes to retain history is not recommended. Instead, consider
  creating a materialized view for your subscription query and configuring the
  history retention period on that view.

#### Clean-up

The history retention period represents the minimum amount of historical data
guaranteed to be retained by Materialize. History clean-up is processed in the
background, so older history may be accessible for the period of time between
when it falls outside the retention period and when it is cleaned up.

## Enabling durable subscriptions in your application

1. In Materialize, configure the history retention period for the object(s)
queried in the `SUBSCRIBE`. Choose a duration you expect will allow you to
recover in case of connection drops. One hour (`1h`) is a good place to start,
though you should be mindful of the [impact](#considerations) of increasing an
object's history retention period.

1. In order to restart your application without losing or re-snapshotting data
after a connection drop, you need to store the latest timestamp processed for
the subscription (either in Materialize, or elsewhere in your application
state). This will allow you to resume using the retained history upstream.

1. The first time you start the subscription, run the following
continuous query against Materialize in your application code:

   ```mzsql
   SUBSCRIBE (<your query>) WITH (PROGRESS, SNAPSHOT true);
   ```

   If you do not need a full snapshot to bootstrap your application,  change
   this to `SNAPSHOT false`.

1. As results come in continuously, buffer the latest results in memory until
you receive a [progress](/sql/subscribe#progress) message. At that point, the
data up until the progress message is complete, so you can:

   1. Process all the buffered data in your application.
   1. Persist the `mz_timestamp` of the progress message.

1. To resume the subscription in subsequent restarts, use the following
continuous query against Materialize in your application code:

   ```mzsql
   SUBSCRIBE (<your query>) WITH (PROGRESS, SNAPSHOT false) AS OF <last_progress_mz_timestamp - 1>;
   ```

   Note the subtraction of `1` from the last received progress timestamp. By
   default (i.e., `SNAPSHOT true`), `SUBSCRIBE` begins by emitting a snapshot at
   the `AS OF` timestamp (if specified) and then emits subsequent updates as
   they occur. However, when `SNAPSHOT false` is set, the snapshot is not
   emitted, and `SUBSCRIBE` emits only updates subsequent to the snapshot; i.e.,
   updates with timestamp greater than the `AS OF` timestamp. To include updates
   that occurred at the last progress timestamp, subtract `1` from the last
   progress timestamp.

   If you're subscribing _directly_ to a collection, as in `SUBSCRIBE TO <your
   collection> WITH (PROGRESS, SNAPSHOT false) AS OF <time>`, Materialize will
   only fetch the recent data for that query from storage, which can make this
   resumption fairly quick. However, subscribing to a query (`SUBSCRIBE TO
   SELECT... WITH (PROGRESS, SNAPSHOT false) AS OF <time>` will build a new
   dataflow that needs to rehydrate, which can be slower. For details, see
   [`SUBSCRIBE`](/sql/subscribe/#snapshot).

   In a similar way, as results come in continuously, buffer the latest results
   in memory until you receive a [progress](/sql/subscribe#progress) message. At that point,
   the data up until the progress message is complete, so you can:

   1. Process all the buffered data in your application.
   1. Persist the `mz_timestamp` of the progress message.

   You can tweak the flush interval at which you durably record the latest
   progress timestamp, if every progress message is too frequent.

### Note about idempotency

The guidance above recommends you buffer data in memory until receiving a
progress message, and then persist the data and progress message `mz_timestamp`
at the same time. This is to ensure data is processed **exactly once**.

In the case that your application crashes and you need to resume your subscription using the
persisted progress message `mz_timestamp`:
* If you were processing data in your application before persisting the subsequent progress message's `mz_timestamp`: you may end up processing duplicate data.
* If you were persisting the progress message's `mz_timestamp` before processing all the
buffered data from before that progress message: you may end up dropping some data.

As a result, to guarantee that the data processing occurs only once after your
application crashes, you must write the progress message `mz_timestamp` and all
buffered data **together in a single transaction**.

---

## Foreign data wrapper (FDW) 

Materialize can be used as a remote server in a PostgreSQL foreign data wrapper
(FDW). This allows you to query any object in Materialize as foreign tables from
a PostgreSQL-compatible database. These objects appear as part of the local
schema, making them accessible over an existing Postgres connection without
requiring changes to application logic or tooling.

## Prerequisite

1. In Materialize, create a dedicated service account `fdw_svc_account` as an
   **Organization Member**. For details on setting up a service account, see
   [Create a service
   account](https://materialize.com/docs/manage/users-service-accounts/create-service-accounts/)

   > **Tip:** Per the linked instructions, be sure you connect at least once with the new
>    service account to finish creating the new account. You will also need the
>    connection details (host, port, password) when setting up the foreign server
>    and user mappings in PostgreSQL.

1. After you have connected at least once with the new service account to finish
   the new account creation, modify the `fdw_svc_account` role:

   1. Set the default cluster to the name of your serving cluster:

      ```mzsql
      ALTER ROLE fdw_svc_account SET CLUSTER = <serving_cluster>;
      ```

   1. [Grant `USAGE` privileges](/sql/grant-privilege/) on the serving cluster,
      and the database and schema of your views and materialized views.

      ```mzsql
      GRANT USAGE ON CLUSTER <serving_cluster> TO fdw_svc_account;
      GRANT USAGE ON DATABASE <db_name> TO fdw_svc_account;
      GRANT USAGE ON SCHEMA <db_name.schema_name> TO fdw_svc_account;
      ```

   1. [Grant `SELECT` privileges](/sql/grant-privilege/) to the various
      view(s)/materialized view(s):

      ```mzsql
      GRANT SELECT ON <db_name.schema_name.view_name>, <...> TO fdw_svc_account;
      ```

## Setup FDW in PostgreSQL

**In your PostgreSQL instance**:

1. If not installed, create a `postgres_fdw` extension in your database:

   ```mzsql
   CREATE EXTENSION postgres_fdw;
   ```

1. Create a foreign server to your Materialize, substitute your [Materialize
   connection details](/developer-tools/console/connect/).

   ```mzsql
   CREATE SERVER remote_mz_server
      FOREIGN DATA WRAPPER postgres_fdw
      OPTIONS (host '<host>', dbname '<db_name>', port '6875');
   ```

1. Create a user mapping between your PostgreSQL user and the Materialize
   `fdw_svc_account`:

   ```mzsql
   CREATE USER MAPPING FOR <postgres_user>
      SERVER remote_mz_server
      OPTIONS (user 'fdw_svc_account', password '<service_account_password>');
   ```

1. For each view/materialized view you want to access, create the foreign table
   mapping (you can use the [data explorer](/developer-tools/console/data/) to get the column
   detials)

   ```mzsql
   CREATE FOREIGN TABLE <local_view_name_in_postgres> (
            <column> <type>,
            ...
        )
   SERVER remote_mz_server
   OPTIONS (schema_name '<schema>', table_name '<view_name_in_Materialize>');
   ```

1. Once created, you can select from within PostgreSQL:

   ```mzsql
   SELECT * from <local_view_name_in_postgres>;
   ```

---

## Isolation levels

An *isolation level* determines which effects of concurrent transactions are
visible to a transaction during its execution.

## Supported isolation levels

Materialize accepts the following isolation levels for your SQL transactions
against Materialize:

| Isolation level | Behavior in Materialize |
| --- | --- |
| [**Strict Serializable**](#strict-serializable) | **Default.** Provides serializability and linearizability. |
| [**Serializable**](#serializable) | Provides serializability but not linearizability. |
| [**Bounded Staleness `<duration>`**](#bounded-staleness) | Serves reads at a timestamp at most `<duration>` stale; never blocks, errors if the bound cannot be met. |
| Read Uncommitted, Read Committed, Repeatable Read | Accepted for compatibility; treated as Serializable. |

## Serializable

Serializable prevents the following three phenomena[^1]:

| Phenomenon | Description |
| --- | --- |
| **P1 (Dirty read)** | A transaction **T1** modifies a row; another transaction **T2** reads the row before **T1** commits. If **T1** rolls back, **T2** has read a row that was never committed. |
| **P2 (Non-repeatable read)** | A transaction **T1** reads a row; another transaction **T2** modifies or deletes that row and commits. If **T1** attempts to reread the row, it may see the modified value or discover that the row no longer exists.|
| **P3 (Phantom)** | A transaction **T1** reads a set of rows that match a specific search condition; another transaction **T2** inserts rows that also match the condition and commits. If **T1** repeats the read with the same search condition, it gets a different set of rows. |

[^1]: Phenomenon descriptions adapted from ISO/IEC 9075-2:1999 (E), §4.32
    "SQL-transactions."

Serializable also guarantees that the result of concurrently executing
transactions is equivalent to some serial execution of those transactions. A
serial execution is one in which each transaction completes before the next one
begins. However, Serializable does not guarantee
[linearizability](https://jepsen.io/consistency/models/linearizable); that is,
it does not guarantee that the serial order matches the real-time order of the
transactions. For example, if transaction **T1** completes before transaction
**T2** begins in real time, the result may be equivalent to a serial execution
in which **T2** executes before **T1**.

Non-linearizable orderings are more likely to occur when querying indexes and
materialized views with large propagation delays. For example, suppose
transaction **T1** queries table `t` and is followed in real time by transaction
**T2**, which queries a computationally expensive materialized view `mv` defined
over `t`. If the two transactions execute sufficiently close together, `mv` may
not yet reflect the latest updates to `t` that **T1** observed, so **T2** may
not observe all rows visible to **T1**.

### Logical timestamp selection {#serializable-logical-timestamp-selection}

When using the [serializable](/serve-results/isolation-level#serializable)
isolation level, the logical timestamp may be arbitrarily ahead of or behind the
system clock. For example, at a wall clock time of 9pm, Materialize may choose
to execute a serializable query as of logical time 8:30pm, perhaps because data
for 8:30–9pm has not yet arrived. In this scenario, `now()` would return 9pm,
while `mz_now()` would return 8:30pm.

## Strict Serializable

Strict Serializable provides all the guarantees of Serializable isolation and
additionally guarantees
[linearizability](https://jepsen.io/consistency/models/linearizable). With
linearizability, the serial order matches the real-time order of the
transactions. For example, if transaction **T1** completes before transaction
**T2** begins in real time, the result is equivalent to a serial execution in
which **T1** executes before **T2**.

More concretely, suppose transaction **T1** queries table `t` and is followed in
real time by transaction **T2**, which queries a computationally expensive
materialized view `mv` defined over `t`. Under Strict Serializable, **T2** is
guaranteed to observe all rows visible to **T1**.

The linearizable guarantee applies only to transactions (including single-statement SQL queries, which are implicitly single-statement transactions), not to data written while ingesting from upstream sources.

- If a piece of data has been fully ingested from an upstream source, it is not
  guaranteed to appear in the next read transaction. See [real-time
  recency](#real-time-recency) for more details.

- However, once that data is included in the results of a read transaction, all
  subsequent read transactions are guaranteed to see it.

### Logical timestamp selection {#strict-serializable-logical-timestamp-selection}

When using the [strict
serializable](/serve-results/isolation-level#strict-serializable) isolation level,
Materialize attempts to keep the logical timestamp reasonably close to wall
clock time. In most cases, the logical timestamp of a query will be within a few
seconds of the wall clock time. For example, when executing a strict
serializable query at a wall clock time of 9pm, Materialize will choose a
logical timestamp within a few seconds of 9pm, even if data for 8:30–9pm has not
yet arrived and the query will need to block until the data for 9pm arrives. In
this scenario, both `now()` and `mz_now()` would return 9pm.

### Real-time recency

Materialize offers a form of "end-to-end linearizability" known as real-time
recency. When using real-time recency, all client-issued `SELECT` statements
include at least all data visible to Materialize in any external source (i.e.,
sources created with `CREATE SOURCE` that use `CONNECTION`s, such as Kafka,
MySQL, and PostgreSQL sources) after Materialize receives the query. This is
what we mean by linearizable––the results are guaranteed to contain all visible
data according to physical time.

For example, real-time recency ensures that if you have just performed an
`INSERT` into a PostgreSQL database that Materialize ingests as a source, all of
your real-time recency queries will include the just-written data in their
results.

Note that real-time recency only guarantees that the results will contain _at
least_ the data visible to Materialize when we receive the query. We cannot
guarantee that the results will contain _only_ the data visible when Materialize
receives the query. For instance, the rate at which Materialize ingests data
might include additional data made visible after the timestamp we determined to
be "real-time recent." Another example is that, due to network latency, the
timestamp from the external system that we determine to be "real-time recent"
might be later (i.e. include more data) than you expected.

Because Materialize waits until it ingests the data from the external system,
real-time recency queries can have additional latency. This latency is
introduced by both the time it takes us to ingest and commit data from the
source and the time spent communicating with it to determine what data it has
made available to us (e.g., querying PostgreSQL for the replication slot's LSN).

**Details**

-   Real-time recency is only available with sessions running at the [strict
    serializable isolation level](#strict-serializable).
-   Enable this feature per session using `SET real_time_recency = true`.
-   Control the timeout for connecting to the external source to determine the
    timestamp with the `real_time_recency_timeout` session variable.
-   Real-time recency queries only guarantee visibility of data from external
    systems (e.g., sources like Kafka, MySQL, and PostgreSQL). Real-time recency
    queries do not offer any form of guarantee when querying Materialize-local
    objects, such as [`LOAD GENERATOR`](/sql/create-source/load-generator/)
    sources or system tables.
-   Each real-time recency query connects to each external source transitively
    referenced in the query. The more external sources that are referenced, the
    greater the likelihood of latency caused by the network or ingestion rates.
-   Materialize doesn't currently offer a mechanism to provide a "lower bound"
    on the data we consider to be "real-time recent" in an external source.
    Real-time recency queries return at least all data visible to Materialize
    when our client connection communicates with the external system.

## Bounded Staleness

The Bounded Staleness isolation level lets you trade exact freshness for
predictable latency. A query under bounded staleness is served at a timestamp
that is at most `<duration>` stale—but never blocks waiting for input
collections to catch up. If no timestamp within `<duration>` of "now" is
available, the query errors immediately.

This sits between [Serializable](#serializable) (no freshness ceiling) and
[Strict Serializable](#strict-serializable) (always freshest, may wait for
inputs to advance) on the freshness/latency spectrum. What distinguishes
bounded staleness is that it never waits on input frontiers — it errors
instead.

### Syntax

```mzsql
SET TRANSACTION_ISOLATION TO 'bounded staleness <duration>';
```

`<duration>` is a duration string like `5s`, `500ms`, or `1m 30s` (compact
forms like `1m30s` are also accepted). It must be greater than `0`.

Bounded staleness is set through the `transaction_isolation` session variable,
as shown above. Because it carries a duration, it cannot be set via the
`BEGIN ... ISOLATION LEVEL` keyword form, which only accepts the standard
isolation-level names.

For example:

```mzsql
-- Read data no more than 5 seconds stale, never block.
SET TRANSACTION_ISOLATION TO 'bounded staleness 5s';

-- A tighter bound for dashboards.
SET TRANSACTION_ISOLATION TO 'bounded staleness 250ms';
```

### Behavior

When a query runs under bounded staleness, Materialize picks the freshest
timestamp at which every queried collection has data, subject to the constraint
that the timestamp is no more than `<duration>` stale relative to the current
logical time. The query never blocks waiting for sources, materialized views,
or indexes to advance. If even the freshest available timestamp is more than
`<duration>` stale, the query errors with `SQLSTATE 40001`
(`serialization_failure`):

```
ERROR: cannot serve query under bounded staleness 5s; freshest available
       timestamp is 7000ms older than the bound
```

`40001` is a serialization failure; how to react is up to the application.
Common responses include retrying, falling back to a different isolation level,
or surfacing a "data unavailable" state.

### Restrictions

- **Read-only.** Writes (`INSERT`, `UPDATE`, `DELETE`, `COPY FROM`) are not
  permitted under bounded staleness. The first write in a session running at
  this isolation level errors.

- **Mutually exclusive with `real_time_recency`.** Setting both errors at
  session-variable validation time.

- **Single timeline.** Bounded staleness only applies to queries on the
  standard wall-clock timeline. Queries that touch other timelines error at
  planning time.

- **Bound must be greater than `0`.** A bound of zero is rejected; use
  [Strict Serializable](#strict-serializable) if you need exact freshness.

### When to use Bounded Staleness

Pick bounded staleness when predictable latency matters more than perfect
freshness, and "data is too stale" is a more useful signal than blocking.
Common cases: dashboards, metric panels, alert evaluation.

- Prefer [Strict Serializable](#strict-serializable) when you need
  linearizable, end-to-end fresh reads, or when your application is willing to
  wait for the freshest data.

- Prefer [Serializable](#serializable) when you do not need a freshness bound
  at all and want the simplest, lowest-latency reads.

- Bounded staleness is read-only: if your session needs writes, use one of the
  other isolation levels.

## Isolation levels and query latency

Strict Serializable provides stronger consistency guarantees but may have slower
reads than Serializable.

- **Strict Serializable** (the default) may need to wait for recent writes to
  propagate through materialized views and indexes before serving a read, so
  that the read reflects the real-time order of transactions.

  - [Real-time recency](#real-time-recency) (available only with Strict
    Serializable) introduces additional latency, since Materialize waits to
    determine and ingest the latest data available in upstream sources before
    serving the query.

- **Serializable** does not wait for writes to propagate. It reads a consistent
  (but possibly slightly stale) snapshot, which avoids that latency at the cost
  of linearizability. However, if a consistent snapshot is not available, the
  query blocks until one becomes available.

- **Bounded Staleness** never waits for writes to propagate. It serves the
  freshest consistent snapshot within the staleness bound, and errors
  immediately when no such snapshot exists instead of blocking.

## Setting isolation level

> **Tip:** Materialize recommends starting with the default Strict Serializable isolation
> level.

You can set the isolation level using the session-level [configuration parameter
`TRANSACTION_ISOLATION`](/sql/set/); for example:

```mzsql
SET TRANSACTION_ISOLATION TO 'STRICT SERIALIZABLE';
```

For `STRICT SERIALIZABLE` and `SERIALIZABLE`, you can also set the isolation
level for an explicit transaction block as part of the [`BEGIN`
statement](/sql/begin); for example:

```mzsql
BEGIN ISOLATION LEVEL STRICT SERIALIZABLE;
--- ...
--- ...
--- ...
COMMIT;
```

## Learn more

Check out:

-   [PostgreSQL documentation](https://www.postgresql.org/docs/current/transaction-iso.html) for more information on
    isolation levels.
-   [Jepsen Consistency Models documentation](https://jepsen.io/consistency) for more information on consistency models.

---

## SQL clients

Materialize is **wire-compatible** with PostgreSQL, which means it integrates
with many SQL clients that support PostgreSQL. In this guide, we’ll cover how to
connect to your Materialize region using some common SQL clients.

## Connection parameters

You can find the credentials for your Materialize region in the
[Materialize console](/developer-tools/console/), under **Connect
externally** in the navigation bar.

Field             | Value
----------------- | ----------------
Host              | Materialize host name.
Port              | **6875**
Database name     | Database to connect to (default: **materialize**).
Database username | Materialize user.
Database password | App password for the Materialize user.
SSL mode          | **Require**

Before connecting, double-check that you've created an **app-password** for your
user. This password is auto-generated, and prefixed with `mzp_`.

### Runtime connection parameters

> **Warning:** Parameters set in the connection string work for the **lifetime of the
> session**, but do not affect other sessions. To permanently change the default
> value of a configuration parameter for a specific user (i.e. role), use the
> [`ALTER ROLE...SET`](/sql/alter-role) command.

You can pass runtime connection parameters (like `cluster`, `isolation_level`,
or `search_path`) to Materialize using the [`options` connection string
parameter](https://www.postgresql.org/docs/14/libpq-connect.html#LIBPQ-PARAMKEYWORDS),
or the [`PGOPTIONS` environment variable](https://www.postgresql.org/docs/16/config-setting.html#CONFIG-SETTING-SHELL).
As an example, to specify a different cluster than the default defined for the
user and set the transactional isolation to serializable on connection using
`psql`:

```bash
# Using the options connection string parameter
psql "postgres://<MZ_USER>@<MZ_HOST>:6875/materialize?sslmode=require&options=--cluster%3Dprod%20--transaction_isolation%3Dserializable"
```

```bash
# Using the PGOPTIONS environment variable
PGOPTIONS='--cluster=prod --transaction_isolation=serializable' \
psql \
    --username=<MZ_USER> \
    --host=<MZ_HOST> \
    --port=6875 \
    --dbname=materialize
```

## Tools

### DataGrip

> **Tip:** Integration with DataGrip/WebStorm is currently limited. Certain features --
> such as the schema explorer, database introspection, and various metadata panels
> -- may not work as expected with Materialize because they rely on
> PostgreSQL-specific queries that use unsupported system functions (e.g.,
> `age()`) and system columns (e.g., `xmin`).
> As an alternative, you can [use the JDBC metadata
> introspector](https://www.jetbrains.com/help/datagrip/cannot-find-a-database-object-in-the-database-tree-view.html#temporarily-enable-introspection-with-jdbc-metadata).
> To use the JDBC metadata instrospector, from your data source properties, in the
> **Advanced** tab, select **Introspect using JDBC Metadata** from the **Expert
> options** list. For more information, see the [DataGrip
> documentation](https://www.jetbrains.com/help/datagrip/cannot-find-a-database-object-in-the-database-tree-view.html#temporarily-enable-introspection-with-jdbc-metadata).

To connect to Materialize using [DataGrip](https://www.jetbrains.com/help/datagrip/connecting-to-a-database.html),
follow the documentation to [create a connection](https://www.jetbrains.com/help/datagrip/connecting-to-a-database.html)
and use the **PostgreSQL database driver** with the credentials provided in the
Materialize console.

<img width="1131" alt="DataGrip Materialize Connection Details" src="https://user-images.githubusercontent.com/21223421/218108169-302c8597-35a9-4dce-b16d-050f49538b9e.png">

[use the JDBC metadata
introspector]:

### DBeaver

**Minimum requirements:** DBeaver 23.1.3

To connect to Materialize using [DBeaver](https://dbeaver.com/docs/wiki/),
follow the documentation to [create a connection](https://dbeaver.com/docs/wiki/Create-Connection/)
and use the **Materialize database driver** with the credentials provided in the
Materialize console.

<img width="1314" alt="Connect using the credentials provided in the Materialize console" src="https://github.com/MaterializeInc/materialize/assets/23521087/ae98dc45-2e1a-4e78-8ca0-e8d53beed30f">

The Materialize database driver depends on the [PostgreSQL JDBC driver](https://jdbc.postgresql.org/download.html).
If you don't have the driver installed locally, DBeaver will prompt you to
automatically download and install the most recent version.

#### Connect to a specific cluster

By default, Materialize connects to the [pre-installed `quickstart` cluster](/sql/show-clusters/#pre-installed-clusters).
To connect to a specific [cluster](/fundamentals/concepts/clusters), you must
define a bootstrap query in the connection initialization settings.

<br>

1. Click on **Connection details**.

1. Click on **Connection initialization settings**.

1. Under **Bootstrap queries**, click **Configure** and add a new SQL query that
sets the active cluster for the connection:

    ```mzsql
    SET cluster = other_cluster;
    ```

Alternatively, you can change the default value of the `cluster` configuration
parameter for a specific user (i.e. role) using the [`ALTER
ROLE...SET`](/sql/alter-role) command.

#### Show system objects

By default, DBeaver hides system catalog objects in the database explorer. This
includes tables, views, and other objects in the `mz_catalog` and `mz_internal`
schemas.

To show system objects in the database explorer:

1. Right-click on the database connection in the **Database Navigator**.
1. Click on **Edit Connection**.
1. In the **Connection settings** tab, select **General**.
1. Next to the **Navigator view**, click **Customize**.
1. In the **Navigator settings** dialog, check the **Show system objects** checkbox.
1. Click **OK**.

### TablePlus

> **Note:** As we work on extending the coverage of `pg_catalog` in Materialize,
> some TablePlus features might not work as expected.

To connect to Materialize using [TablePlus](https://tableplus.com/),
follow the documentation to [create a connection](https://docs.tableplus.com/gui-tools/manage-connections#create-a-connection)
and use the **PostgreSQL database driver** with the credentials provided in the
Materialize console.

<img width="1440" alt="Screenshot 2023-12-28 at 18 45 11" src="https://github.com/MaterializeInc/materialize/assets/23521087/c530769e-3445-49c8-8f36-9f7166352ac4">

### `psql`

> **Warning:** Not all features of `psql` are supported by Materialize yet, including some backslash meta-commands.

**macOS:**

Start by double-checking whether you already have `psql` installed:

```shell
psql --version
```

Assuming you’ve installed [Homebrew](https://brew.sh/):

```shell
brew install libpq
```

Then symlink the `psql` binary to your `/usr/local/bin` directory:

```shell
brew link --force libpq
```

**Linux:**

Start by double-checking whether you already have `psql` installed:

```shell
psql --version
```

```bash
sudo apt-get update
sudo apt-get install postgresql-client
```

The `postgresql-client` package includes only the client binaries, not the PostgreSQL server.

For other Linux distributions, check out the [PostgreSQL documentation](https://www.postgresql.org/download/linux/).

**Windows:**

Start by double-checking whether you already have `psql` installed:

```shell
psql --version
```

Download and install the [PostgreSQL installer](https://www.postgresql.org/download/windows/) certified by EDB.

## See also

See also the following integration guides for BI tools:

- [Deepnote](/serve-results/bi-tools/deepnote/)
- [Excel](/serve-results/bi-tools/excel/)
- [Hex](/serve-results/bi-tools/hex/)
- [Metabase](/serve-results/bi-tools/metabase/)
- [Power BI](/serve-results/bi-tools/power-bi/)
- [Tableau](/serve-results/bi-tools/tableau/)
- [Looker](/serve-results/bi-tools/looker/)

---

## Troubleshooting

This section contains troubleshooting guides for queries that don't perform as
expected. Each guide starts from a symptom, helps you find the cause with SQL
against the system catalog, and describes how to fix it.

## Troubleshooting guides

| Guide | Description |
|-------|-------------|
| [Slow queries](/serve-results/troubleshooting/slow-queries/) | Find which stage of a query's lifecycle takes the most time, and fix it. Includes a section for self-managed deployments. |
| [Unresponsive queries](/serve-results/troubleshooting/unresponsive-queries/) | Find why a query hangs or never returns, and cancel it. |
| [Expensive queries](/serve-results/troubleshooting/expensive-queries/) | Find queries that use a lot of CPU or memory on a cluster, and reduce their cost. |

## Query history

All three guides use the statement log, which records a sample of the SQL
statements issued against Materialize in the last **24 hours**. You can browse
it in the **Query history** tab of the [Materialize
console](/developer-tools/console/), or query it through
[`mz_internal.mz_recent_activity_log`](/sql/system-catalog/mz_internal/#mz_recent_activity_log).

To query the statement log, connect as a *superuser* or as a user granted the
[`mz_monitor` role](/security/appendix/appendix-built-in-roles/#system-catalog-roles).

Statements are sampled and throttled, so not every statement appears in the
log. In Materialize Cloud, Materialize controls the sample rate and may change
it at any time. In self-managed deployments, the operator sets it.

### Control the sample rate on Materialize Self-Managed

The fraction of statements logged is the smaller of two values:

| Parameter | Scope | Description |
|-----------|-------|-------------|
| `statement_logging_max_sample_rate` | System | Upper bound for every session. `0` disables statement logging. |
| `statement_logging_sample_rate` | Session | Rate the session requests. New sessions start at `statement_logging_default_sample_rate`. |

A higher sample rate makes the log more complete, which helps when you need to
find a specific slow query. The tradeoff is CPU overhead on `environmentd`, which
grows with statement throughput. Separately,
`statement_logging_target_data_rate` caps the bytes written per second, so on a
busy instance some sampled statements are still dropped even at a rate of `1.0`.

To change the system-wide rates, connect as the `mz_system` user and run:

```mzsql
ALTER SYSTEM SET statement_logging_max_sample_rate = 0.5;
ALTER SYSTEM SET statement_logging_default_sample_rate = 0.5;
```

To log every statement in your own session while you debug, run:

```mzsql
SET statement_logging_sample_rate = 1.0;
```

To check the rates in effect:

```mzsql
SHOW statement_logging_max_sample_rate;
SHOW statement_logging_sample_rate;
```

`ALTER SYSTEM SET` takes effect immediately and overrides the Helm chart value.
For the Helm chart settings, storage costs, and how to revert an override, see
[Query History](/self-managed-deployments/query-history/).

For a complete history of DDL statements, use
[`mz_audit_events`](/sql/system-catalog/mz_catalog/#mz_audit_events).

---

## Use BI/data collaboration tools

Materialize uses the PostgreSQL wire protocol, which allows it to integrate out-of-the-box with various BI/data collaboration tools that support PostgreSQL.

To help you get started, the following guides are available:

---

## Use foreign data wrapper (FDW)

Materialize can be used as a remote server in a PostgreSQL foreign data wrapper
(FDW). This allows you to query any object in Materialize as foreign tables from
a PostgreSQL-compatible database. These objects appear as part of the local
schema, making them accessible over an existing Postgres connection without
requiring changes to application logic or tooling.

## Prerequisite

1. In Materialize, create a dedicated service account `fdw_svc_account` as an
   **Organization Member**. For details on setting up a service account, see
   [Create a service
   account](https://materialize.com/docs/manage/users-service-accounts/create-service-accounts/)

   > **Tip:** Per the linked instructions, be sure you connect at least once with the new
>    service account to finish creating the new account. You will also need the
>    connection details (host, port, password) when setting up the foreign server
>    and user mappings in PostgreSQL.

1. After you have connected at least once with the new service account to finish
   the new account creation, modify the `fdw_svc_account` role:

   1. Set the default cluster to the name of your serving cluster:

      ```mzsql
      ALTER ROLE fdw_svc_account SET CLUSTER = <serving_cluster>;
      ```

   1. [Grant `USAGE` privileges](/sql/grant-privilege/) on the serving cluster,
      and the database and schema of your views and materialized views.

      ```mzsql
      GRANT USAGE ON CLUSTER <serving_cluster> TO fdw_svc_account;
      GRANT USAGE ON DATABASE <db_name> TO fdw_svc_account;
      GRANT USAGE ON SCHEMA <db_name.schema_name> TO fdw_svc_account;
      ```

   1. [Grant `SELECT` privileges](/sql/grant-privilege/) to the various
      view(s)/materialized view(s):

      ```mzsql
      GRANT SELECT ON <db_name.schema_name.view_name>, <...> TO fdw_svc_account;
      ```

## Setup FDW in PostgreSQL

**In your PostgreSQL instance**:

1. If not installed, create a `postgres_fdw` extension in your database:

   ```mzsql
   CREATE EXTENSION postgres_fdw;
   ```

1. Create a foreign server to your Materialize, substitute your [Materialize
   connection details](/developer-tools/console/connect/).

   ```mzsql
   CREATE SERVER remote_mz_server
      FOREIGN DATA WRAPPER postgres_fdw
      OPTIONS (host '<host>', dbname '<db_name>', port '6875');
   ```

1. Create a user mapping between your PostgreSQL user and the Materialize
   `fdw_svc_account`:

   ```mzsql
   CREATE USER MAPPING FOR <postgres_user>
      SERVER remote_mz_server
      OPTIONS (user 'fdw_svc_account', password '<service_account_password>');
   ```

1. For each view/materialized view you want to access, create the foreign table
   mapping (you can use the [data explorer](/developer-tools/console/data/) to get the column
   detials)

   ```mzsql
   CREATE FOREIGN TABLE <local_view_name_in_postgres> (
            <column> <type>,
            ...
        )
   SERVER remote_mz_server
   OPTIONS (schema_name '<schema>', table_name '<view_name_in_Materialize>');
   ```

1. Once created, you can select from within PostgreSQL:

   ```mzsql
   SELECT * from <local_view_name_in_postgres>;
   ```

