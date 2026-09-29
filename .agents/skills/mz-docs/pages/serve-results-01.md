<!-- mz-docs page: serve-results -->

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

<!-- mz-docs page: serve-results/adbc -->

# ADBC (Arrow Database Connectivity)
Use the ADBC PostgreSQL driver to pull Materialize results into Apache Arrow

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

<!-- mz-docs page: serve-results/bi-tools -->

# Use BI/data collaboration tools

Querying results from Materialize using external BI/data collaboration tools

Materialize uses the PostgreSQL wire protocol, which allows it to integrate out-of-the-box with various BI/data collaboration tools that support PostgreSQL.

To help you get started, the following guides are available:

<!-- mz-docs page: serve-results/bi-tools/deepnote -->

# Deepnote
How to create collaborative data notebooks with Deepnote
This guide walks you through the steps required to use the collaborative data notebook [Deepnote](https://deepnote.com/) with Materialize.

## Create an integration

1. Sign in to **[Deepnote](https://deepnote.com/)**.
2. Go to the **Workspace integrations** page.
  > **Note:** If you are inside a workspace, in the <svg width="12px" height="12px" stroke="currentColor" fill="currentColor" stroke-width="0.5" viewBox="0 0 24 24" focusable="false" aria-hidden="true" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path></svg>
>  **Menu**, click **Integrations**

1. Click in the **+ Add Integration** button.
2. Search and click the **Materialize** option.
3. Enter the connection fields as follows:
    Field             | Value
    ----------------- | ----------------------
    Integration name  | Materialize.
    Host name         | Materialize host name.
    Port              | **6875**
    Username          | Materialize user.
    Password          | App-specific password.
    Database          | **materialize**
    Cluster           | Your preferred cluster.
4. Click the **Create Integration** button.
5. After a successful test, in the popup dialog, you can either select an existing project or create a new one to continue.

## Configure a custom cluster

To direct queries to a specific cluster, [set the cluster at the role
level](/sql/alter-role) using the following SQL statement:

```sql
ALTER ROLE <your_user> SET CLUSTER = <custom_cluster>;
```

Replace `<your_user>` with the name of your Materialize role and `<custom_cluster>` with the name of the cluster you want to use.

Once set, all new sessions for that user will automatically run in the specified
cluster, eliminating the need to manually specify it in each query or
connection.

## Execute and visualize a query

1. Create a new SQL block.

2. Inside the block, select the new **Materialize** integration and paste the following query:
    ```mzsql
    SELECT
        number,
        row_num
    FROM (
        SELECT
            power(series_number, 2) AS number,
            row_number()
                OVER
                (ORDER BY series_number ASC, series_number DESC)
            AS row_num
        FROM (
            SELECT generate_series(0, 1000) AS series_number
        ) AS subquery
    );
    ```

    This query generates a series of 1000 numbers squared and assigns row numbers to each.
3. Click the **Run Notebook** button.

4. Inside the block, click the <svg height="11px" width="11px" viewBox="0 0 11 11" focusable="false"><path fill="currentColor" d="M0.333252 0.75V9.5C0.333252 10.1376 0.862299 10.6667 1.49992 10.6667H10.2499V9.5H1.49992V0.75H0.333252ZM9.83748 2.08756L7.33325 4.5918L5.58325 2.8418L2.25415 6.1709L3.07902 6.99577L5.58325 4.49154L7.33325 6.24154L10.6624 2.91243L9.83748 2.08756Z"></path></svg>
 **Visualize** button and configure as follows:
   1. In the **Y Axis** options, select the **number** column and set the aggregation to **None**.
   2. In the **X Axis** options, select the **row_num** column and set the aggregation to **None**.

   <img width="1002" alt="Deepnote guide" src="https://github.com/joacoc/materialize/assets/11491779/fdd21c0c-db2f-4096-8d7a-dd38bdfb646d">

### Related pages

For more information about Deepnote and the integration, visit [their documentation.](https://deepnote.com/docs/materialize)

<!-- mz-docs page: serve-results/bi-tools/excel -->

# Excel
Serve data from Materialize into Excel using ODBC
Because Materialize is PostgreSQL wire-compatible, you can use a standard
PostgreSQL ODBC driver to serve data from Materialize into Excel spreadsheets.

> **Note:** The following procedure has only been tested on Windows machines using
> Materialize Cloud.

## Prerequisites

- A Windows machine with Excel.
- Access to your Materialize instance.
- Your Materialize Cloud connection details. For Materialize Cloud, you can find
  the connection details from the Materialize Console under `App Passwords ->
  Connect -> External Tools`.

## Setup guide

### Step 1: Install the Postgres ODBC driver

Install the latest version of the Postgres ODBC driver on your Windows machine from the [PostgreSQL ODBC driver download page](https://odbc.postgresql.org/).

### Step 2: Configure ODBC data source

You can set up your ODBC data source via the Windows Control Panel or via a
`.reg` file.

**Windows Control Panel:**
1. From the Windows control panel, find the `Set up ODBC data sources (64-bit)`
   option (assuming you are using 64-bit version of Excel).

1. If you have successfully installed pgODBC, you should see an option in
   `Create A New Data Source` called `PostgreSQL Unicode(x64)`. Select
   `PostgreSQL Unicode(x64)`.

1. Specify the [connection details for Materialize](/developer-tools/console/connect/). You can
   find the details from the Materialize console under `App Passwords -> Connect
   -> External Tools`. For `Password`, use your App Password (which is shown
   only once during the [service account
   creation](/developer-tools/console/create-new/#create-new-app-password-cloud-only)).

   ![Image of the Materialize Data Source configuration
setup](/images/excel/excel-setup-config.png "Set up Materialize Data Source
configuration.")

1. If you are using a cluster besides `default` for your view, click on
   `Datasource` to get to the **Advanced Options**. Go to `Page 2` and add `set
   cluster = <clustername>;` in the **Connect Settings** field. Click `OK`.

   ![Image of the Advanced Options](/images/excel/excel-advanced-options.png "In
Advanced Options, specify the cluster in the **Connect Settings** field.")

**.reg File:**

If you are deploying to multiple machines and do not want to use the GUI to
create the ODBC settings, you could instead create a `.reg` file to deploy the
registry settings. For example, you can save the following sample content as a
`.reg` file in Windows, updating the:
- `Driver` (path to your psqlODBC installation),
- `Database`,
- `Servername`,
- `Username`,
- `UID`,
- `Password`, and
- `ConnSettings`.

> **Note:** - Passwords stored in `.reg` files are saved in plain text. Restrict access to
> the file.
> - This example creates a User DSN. To create a System DSN, use
> HKEY_LOCAL_MACHINE instead.

```reg {hl_lines="4 19-25"}
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\ODBC\ODBC.INI\mz]
"Driver"="C:\\Program Files\\psqlODBC\\1700\\bin\\psqlodbcw.dll"
"CommLog"="2"
"Debug"="2"
"Fetch"="100"
"UniqueIndex"="0"
"UseDeclareFetch"="0"
"UnknownSizes"="0"
"TextAsLongVarchar"="0"
"UnknownsAsLongVarchar"="0"
"BoolsAsChar"="1"
"Parse"="0"
"MaxVarcharSize"="255"
"MaxLongVarcharSize"="8190"
"ExtraSysTablePrefixes"=""
"Description"=""
"Database"="materialize"
"Servername"="your.materialize.server.name"
"Port"="6875"
"Username"="user@materialize.com"
"UID"="user@materialize.com"
"Password"="my_app_password"
"ConnSettings"="set cluster = default;"
"ReadOnly"="0"
"ShowOidColumn"="0"
"FakeOidIndex"="0"
"RowVersioning"="0"
"ShowSystemTables"="0"
"Protocol"=""
"pqopt"=""
"UpdatableCursors"="1"
"LFConversion"="1"
"TrueIsMinus1"="0"
"BI"="0"
"AB"="0"
"ByteaAsLongVarBinary"="1"
"UseServerSidePrepare"="0"
"LowerCaseIdentifier"="0"
"GssAuthUseGSS"="0"
"SSLmode"="require"
"KeepaliveTime"="-1"
"KeepaliveInterval"="-1"
"XaOpt"="1"
"D6"="-101"
"OptionalErrors"="0"
"BatchSize"="100"
"IgnoreTimeout"="0"
"FetchRefcursors"="0"
```

### Step 3: Connect to Materialize from Excel

1. Open Excel. From the **Data** toolbar, click on `Get Data -> From Other
   Sources -> From ODBC`.

1. Select the Data source name created for Materialize and click `OK`:

   ![Image of Materialize ODBC Connection
   selection](/images/excel/excel-select-mz-source.png "Select the Materialize source
   created earlier.")

1. Select the `Default or Custom` tab, then click `Connect`. The **Navigator**
   pane will open.

1. Use the **Navigator** to select the view whose data you want to load into
   Excel. Click `Load`.

   ![Image of the Excel Navigator](/images/excel/excel-navigate-to-view.png
   "In the Navigator, select the view")

   You should see the data in your Excel spreadsheet.

1. Optional. You can manually click on `Data -> Refresh All` to refresh the
   data.

### Step 4: Configure automatic refresh

To refresh as frequently as once per minute, you can update the refresh
configuration:

1. Open **Query Properties** panel.  Go to `Data -> Queries & Connections`.
   Right click on a specific query and select `Properties`.

   ![Image of opening Query
    Properties](/images/excel/excel-open-query-properties.png "From the Data
    menubar, click Queries & Connections. Right click on your query and select
    Properties").

1. Check `Refresh every _ minutes` and set the frequency and click `OK`.

   ![Image of Query Properties - updated refresh
    rate](/images/excel/excel-query-properties-refresh.png "In Query Properties
    panel, update the Refresh every minutes field.").

To refresh more frequently than once per minute requires a custom VBA script.
See [Custom refresh rate](#custom-refresh-rate) below.

#### Custom refresh rate

For most scenarios, refreshing every minute is sufficient. However, if you need
to refresh more frequently for your use case, you can use a custom VBA script:

> **Note:** When configuring your refresh interval, note that Excel will throw an error
> if a refresh does not complete before the next one begins. Depending on your
> machine, this is typically between 5 and 15 seconds.

1. Press `Alt-F11` to open the VBA editor. On the left side, navigate to the
   VBAProject for your open spreadsheet.

1. Right click on `Microsoft Excel Objects` and select `Insert -> Module`.

   ![Image of VBA editor: Navigate to Insert ->
   Module](/images/excel/excel-vba-module.png "VBA editor: Navigate to Insert
   -> Module").

1. In the module editor, copy and paste the following code. Edit
   the `RefreshPeriod` and `Application.OnTime` values for different refresh
   rates as required.

   > **Note:** When configuring your refresh interval, note that Excel will throw an error
>    if a refresh does not complete before the next one begins. Depending on your
>    machine, this is typically between 5 and 15 seconds.

    ```text {hl_lines="7 13"}
    Sub AutoRefresh()
    ' Set the data connection to refresh every 15 seconds
    Dim conn As WorkbookConnection
    For Each conn In ThisWorkbook.Connections
        With conn.OLEDBConnection
            .BackgroundQuery = True
            .RefreshPeriod = 0.25   ' The property takes minutes as input. 0.25 minutes is equivalent to 15 seconds.
            .Refresh
        End With
    Next conn

    ' Set the macro to run itself again in 15 seconds
    Application.OnTime Now + TimeValue("00:00:15"), "AutoRefresh"
    End Sub
    ```

1. Press `Alt-Q` to close the VBA editor and return to Excel.

1. From Excel, you can use `Alt-F8` to open up the Macro window and run the
   `AutoRefresh` macro.

   ![Image of Macro window -> Run
   AutoRefresh](/images/excel/excel-macro-autorefresh.png "Macro window: run
   AutoRefresh.").

   Excel should now start updating your Materialize data at the refresh rate set
   in the macro.

## Best practices

- **Index your views**: Since Materialize efficiently serves queries from
  indexed views/indexed materialized views, ensure your views are properly
  indexed to support frequent refreshes without impacting performance.

<!-- mz-docs page: serve-results/bi-tools/hex -->

# Hex
How to create collaborative data notebooks with Hex
This guide walks you through the steps required to use the collaborative data notebook [Hex](https://hex.tech/) with Materialize.

## Create an integration

1. Sign in to **[Hex](https://hex.tech/)**.

2. Go to an existing project or create a new one.

3. Go to <svg data-icon="data-sources" height="13" viewBox="0 0 15 15" width="13"><g><path d="M11 2.5L5.5 9.5H9.5L9 13.5L15 6.5H10.5L11 2.5Z" fill="currentColor" opacity="0.2"></path><path clip-rule="evenodd" d="M2.14914 0.609383L2.19234 0.595681C3.37179 0.221591 4.07044 0 7 0C8.04628 0 9.01165 0.0642082 9.8677 0.181908L9.19429 1.10785C8.52823 1.03836 7.79287 1 7 1C4.21744 1 3.57924 1.20334 2.58084 1.52143L2.45136 1.56262C1.90997 1.73427 1.52165 1.92749 1.2791 2.1163C1.03316 2.30775 1 2.44121 1 2.5C1 2.55791 1.03273 2.69091 1.2788 2.88216C1.52136 3.07068 1.90973 3.26364 2.45118 3.43507L2.58077 3.47624C3.57918 3.7939 4.21751 3.997 7 3.997L7.09322 3.99682L6.36859 4.99318C3.96155 4.96242 3.28225 4.74726 2.19282 4.4022L2.14932 4.38843C1.71286 4.25024 1.32321 4.08702 1 3.89705V7.496C1 7.55479 1.03316 7.68825 1.2791 7.8797C1.52165 8.06851 1.90997 8.26173 2.45136 8.43338L2.58084 8.47457L2.58085 8.47457C2.93657 8.5879 3.24656 8.68667 3.6241 8.76686L2.98878 9.64043C2.72618 9.56964 2.47286 9.48929 2.19234 9.40032L2.14914 9.38662C1.71276 9.24826 1.32318 9.08485 1 8.89466V12.492C1 12.5507 1.03312 12.6841 1.27903 12.8755C1.52155 13.0642 1.90987 13.2573 2.45127 13.4289L2.58047 13.4699C3.47562 13.7549 4.08109 13.9477 6.20154 13.9846L6.10171 14.9829C3.90892 14.9399 3.24056 14.728 2.19209 14.3957L2.14923 14.3821C1.54888 14.1919 1.03707 13.9543 0.66491 13.6647C0.296134 13.3777 0 12.9853 0 12.492V2.5C0 2.00679 0.296094 1.61425 0.664835 1.3272C1.03698 1.03751 1.54878 0.79973 2.14914 0.609383ZM4 10L12 0L11 6H16L8 16L9 10H4ZM9.81954 7H13.9194L9.61759 12.3772L10.1805 9H6.08062L10.3824 3.62277L9.81954 7Z" fill="currentColor" fill-rule="evenodd"></path></g></g></svg>
**Data Sources > +Add > Create data connection... > Materialize**.

4. Search and click the **Materialize** option.

5. Enter the connection fields as follows:
    Field               | Value
    ------------------- | ----------------------
    Name                | Materialize.
    Description         | A description you prefer.
    Host & Port         | Materialize host name, and **6875** for the port.
    Database            | **materialize**
    Authentication type | Choose the **Password** option.
    Username            | Materialize user.
    Password            | App-specific password.

6. Click the **Create connection** button.

## Configure a custom cluster

To direct queries to a specific cluster, [set the cluster at the role
level](/sql/alter-role) using the following SQL statement:

```sql
ALTER ROLE <your_user> SET CLUSTER = <custom_cluster>;
```

Replace `<your_user>` with the name of your Materialize role and `<custom_cluster>` with the name of the cluster you want to use.

Once set, all new sessions for that user will automatically run in the specified
cluster, eliminating the need to manually specify it in each query or
connection.

## Execute and visualize a query

1. Create a new SQL cell.

2. Inside the cell, select the new **Materialize** connection and paste the following query:
    ```mzsql
    SELECT
        number,
        row_num
    FROM (
        SELECT
            power(series_number, 2) AS number,
            row_number()
                OVER
                (ORDER BY series_number ASC, series_number DESC)
            AS row_num
        FROM (
            SELECT generate_series(0, 1000) AS series_number
        ) AS subquery
    );
    ```

    This query generates a series of 1000 numbers squared and assigns row numbers to each.
3. Click the <svg color="#868ea4" data-icon="run" height="16" viewBox="0 0 13 13" width="16"><desc>dynamic</desc><g stroke-width="1"><g><path d="M4.5 12C4.5 12.1844 4.60149 12.3538 4.76407 12.4408C4.92665 12.5278 5.12392 12.5183 5.27735 12.416L11.2773 8.41603C11.4164 8.32329 11.5 8.16718 11.5 8C11.5 7.83282 11.4164 7.67671 11.2773 7.58397L5.27735 3.58397C5.12392 3.48169 4.92665 3.47215 4.76407 3.55916C4.60149 3.64617 4.5 3.8156 4.5 4V12Z" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-linejoin="round"></path></g></g></svg>
 **Run** button.

4. Inside the cell, click the **Chart** button and configure as follows:
   1. In the **X Axis** options, select the **row_num** column.
   2. In the **Y Axis** options, select the **number** column.

   <img width="1091" alt="Hex" src="https://github.com/MaterializeInc/materialize/assets/11491779/2da93aad-9332-4d7c-a407-c068a856b9ed">

### Related pages

For more information about Hex and data connections, visit [their documentation.](https://learn.hex.tech/docs/connect-to-data/data-connections/overview)

<!-- mz-docs page: serve-results/bi-tools/looker -->

# Looker
How to create dashboards with Looker
You can use [Looker](https://cloud.google.com/looker-bi) to create dashboards
based on the data maintained in Materialize.

## Database connection details

To set up a connection from Looker to Materialize, use the native
[PostgreSQL 9.5+ database dialect](https://cloud.google.com/looker/docs/db-config-postgresql)
with the following parameters:

Field                  | Value
---------------------- | ----------------
Dialect                | **PostgreSQL 9.5+**.
Host                   | Materialize host name.
Port                   | **6875**
Database               | **materialize**
Schema                 | **public**
Database username      | Materialize user.
Database password      | App-specific password.

![Connect using the credentials provided in the Materialize console](https://github-production-user-asset-6210df.s3.amazonaws.com/21223421/272911799-2525c5ae-4594-4d33-bdfa-c20af835c7c5.png)

## Configure a custom cluster

To direct queries to a specific cluster, [set the cluster at the role
level](/sql/alter-role) using the following SQL statement:

```sql
ALTER ROLE <your_user> SET CLUSTER = <custom_cluster>;
```

Replace `<your_user>` with the name of your Materialize role and `<custom_cluster>` with the name of the cluster you want to use.

Once set, all new sessions for that user will automatically run in the specified
cluster, eliminating the need to manually specify it in each query or
connection.

## Known limitations

When using Looker with Materialize, be aware of the following limitations:

1. **Connection Test Error**: You might encounter this error when testing the connection to Materialize from Looker:

   ```
   Test kill: Cannot cancel queries: Query could not be found in database.
   ```

   This error occurs because Looker attempts to run a test query cancellation, which checks for `pg_stat_activity` (not currently supported in Materialize).

   While this error can be safely ignored and doesn't impact most Looker functionality, there are workarounds for query cancellation if you need to stop a running query:

   a. Use `pg_cancel_backend` in Materialize:

      ```sql
      SELECT pg_cancel_backend(connection_id)
      FROM mz_sessions
      WHERE id = 'your_session_id';
      ```

   b. Via the Materialize Console:
      - Go to [Materialize Console](/developer-tools/console/)
      - Navigate to Query History
      - Filter by 'Running' queries
      - Click on the query you want to cancel
      - Select "Request Cancellation"

2. **Symmetric Aggregates**: Looker uses symmetric aggregates, which rely on types and operations not fully supported in Materialize:

   - Materialize doesn't support the `BIT` type used by Looker for symmetric aggregates.
   - Looker may use various aggregations (e.g., `SUM DISTINCT`, `AVG DISTINCT`) for symmetric aggregates.
   - You can disable symmetric aggregates in Looker if needed. For instructions, refer to the [Looker documentation on disabling symmetric aggregates](https://cloud.google.com/looker/docs/reference/param-explore-symmetric-aggregates#not_all_database_dialects_support_median_and_percentile_measure_types_with_symmetric_aggregates).
   - Looker is fully functional for non-symmetric aggregations when visualizing Materialize data.

3. **Handling Symmetric Aggregates**:

   a. Test query performance with and without symmetric aggregates to determine the optimal configuration.

   b. If you encounter performance issues, disable symmetric aggregates in your Looker setup using the link provided above.

   c. For use cases requiring symmetric aggregates, contact Materialize support for optimization guidance.

<!-- mz-docs page: serve-results/bi-tools/metabase -->

# Metabase
How to create real-time dashboards with Metabase
You can use [Metabase](https://www.metabase.com/) to create real-time dashboards
based on the data maintained in Materialize.

## Database connection details

To set up a connection from Metabase to Materialize, use the native
[PostgreSQL database driver](https://www.metabase.com/docs/latest/administration-guide/databases/postgresql.html)
with the following parameters:

Field             | Value
----------------- | ----------------
Database type     | **PostgreSQL**
Host              | Materialize host name.
Port              | **6875**
Database name     | **materialize**
Database username | Materialize user.
Database password | App-specific password.
SSL mode          | Require

For more details and troubleshooting, check the
[Metabase documentation](https://www.metabase.com/docs/latest/administration-guide/databases/postgresql.html).

## Configure a custom cluster

To direct queries to a specific cluster, [set the cluster at the role
level](/sql/alter-role) using the following SQL statement:

```sql
ALTER ROLE <your_user> SET CLUSTER = <custom_cluster>;
```

Replace `<your_user>` with the name of your Materialize role and `<custom_cluster>` with the name of the cluster you want to use.

Once set, all new sessions for that user will automatically run in the specified
cluster, eliminating the need to manually specify it in each query or
connection.

## Refresh rate

By default, the lowest [refresh rate](https://www.metabase.com/docs/latest/users-guide/07-dashboards.html#auto-refresh)
for Metabase dashboards is 1 minute. You can manually set this to a lower
interval by adding `#refresh=1` (as an example, for a `1` second interval) to
the end of the URL, and opening the modified URL in a new tab.

Because Metabase queries are simply reading data out of self-updating views in
Materialize, setting your dashboards to auto-refresh at lower rates should not
have a significant impact on database performance. To minimize this impact, we
recommend carefully choosing an [indexing strategy](/sql/create-index/)
for any objects serving results to Metabase.

[//]: # "TODO(morsapaes) Once we revamp quickstarts, add Related pages section
pointing to a quickstart that uses Metabase"

<!-- mz-docs page: serve-results/bi-tools/power-bi -->

# Power BI
How to create dashboards with Power BI
You can use [Power BI](https://powerbi.microsoft.com/) to create dashboards
based on the data maintained in Materialize.

## Database connection details

To set up a connection from Power BI to Materialize, use the native
[PostgreSQL database driver](https://learn.microsoft.com/en-us/power-query/connectors/postgresql#connect-to-a-postgresql-database-from-power-query-desktop)
with the following parameters:

Field                  | Value
---------------------- | ----------------
Database type          | **PostgreSQL database**
Server                 | Your Materialize host name followed by `:6875`<br> For example: `id.us-east-1.aws.materialize.cloud:6875`
Database               | **materialize**
Data Connectivity mode | **DirectQuery**
Database username      | Materialize user.
Database password      | App-specific password.

![Connect using the credentials provided in the Materialize console](https://github-production-user-asset-6210df.s3.amazonaws.com/21223421/266625944-de7dfdc6-7a94-4e87-ac0a-01e104512ffe.png)

## Configure a custom cluster

To direct queries to a specific cluster, [set the cluster at the role
level](/sql/alter-role) using the following SQL statement:

```sql
ALTER ROLE <your_user> SET CLUSTER = <custom_cluster>;
```

Replace `<your_user>` with the name of your Materialize role and `<custom_cluster>` with the name of the cluster you want to use.

Once set, all new sessions for that user will automatically run in the specified
cluster, eliminating the need to manually specify it in each query or
connection.

## Troubleshooting

Errors like the following indicate that there is a problem with the connection settings:

1. `A non-recoverable error happened during a database lookup.`

    If you see this error, check that the server name is correct and that you are using port `6875`. Note that the server name should not include the protocol (`http://` or `https://`), and should not include a trailing slash (`/`) or the database name.

2. `PostgreSQL: No password has been provided but the backend requires one (in cleartext)`

    If you see this error, check that you have entered the correct password. If you are using an app-specific password, make sure that you have not included any spaces or other characters that are not part of the password. If the issue persists, try the following:

    - Go to **File**
    - Options and settings
    - Data source settings
    - Delete any references for the Materialize host from the data source list
    - Try to connect again

For more details and troubleshooting, check the
[Power BI documentation](https://learn.microsoft.com/en-us/power-query/connectors/postgresql#troubleshooting).

## Known limitations

When you connect to Materialize from Power BI, you will get a list of your tables and views.

However, [Power BI does not display materialized views](https://ideas.fabric.microsoft.com/ideas/idea/?ideaid=92420736-afdc-45b9-8962-743a53acfa66) in that list.

To work around this Power BI limitation, you can use one of the following options:

1. Create a view that selects from the materialized view, and then use the view in Power BI.

    For example, if you have a materialized view called `my_view`, you can create a view called `my_view_bi` with the following SQL:

    ```mzsql
    CREATE VIEW my_view_bi AS SELECT * FROM my_view;
    ```

    Then, in Power BI, you can use the `my_view_bi` view.

2. If applicable, instead of using a materialized view, create a view with an [index](/sql/create-index) instead.

3. Use the [Power BI Native query folding](https://learn.microsoft.com/en-us/power-query/connectors/postgresql#native-query-folding) to write your own query rather than using the Power BI UI. For example:

    ```
    = Value.NativeQuery(Source, "select * from my_view;")
    ```

<!-- mz-docs page: serve-results/bi-tools/tableau -->

# Tableau
How to create real-time dashboards with Tableau
You can use [Tableau Cloud](https://www.tableau.com/products/cloud-bi) and
[Tableau Desktop](https://www.tableau.com/products/desktop) to create real-time
dashboards based on the data maintained in Materialize.

## Tableau Cloud

### Database connection details

To set up a connection from Tableau Cloud to Materialize, use the native
[PostgreSQL database connector](https://help.tableau.com/current/pro/desktop/en-us/examples_postgresql.htm)
with the following parameters:

Field             | Value
----------------- | ----------------
Server            | Materialize host name.
Port              | **6875**
Database          | **materialize**
Username          | Materialize user.
Password          | App-specific password.
Require SSL       | ✓

For more details and troubleshooting, check the
[Tableau documentation](https://help.tableau.com/current/pro/desktop/en-us/examples_postgresql.htm).

[//]: # "TODO(morsapaes) Clarify minimum refresh rate and details about live
connections"

## Tableau Desktop

### Setup

**macOS:**

To set up a connection from Tableau Desktop to Materialize, you must:

1. Download the [Java 8 JDBC driver for PostgreSQL](https://jdbc.postgresql.org/download/)
1. Copy the `.jar` file to the following directory (which may have to be created manually):

   `~/Library/Tableau/Drivers`

**Linux:**

To set up a connection from Tableau Desktop to Materialize, you must:

1. Download the [Java 8 JDBC driver for PostgreSQL](https://jdbc.postgresql.org/download/)
1. Copy the `.jar` file to the following directory (which may have to be created manually):

   `/opt/tableau/tableau_driver/jdbc`

**Windows:**

To set up a connection from Tableau Desktop to Materialize, you must:

1. Download the [Java 8 JDBC driver for PostgreSQL](https://jdbc.postgresql.org/download/)
1. Copy the `.jar` file to the following directory (which may have to be created manually):

   `C:\Program Files\Tableau\Drivers`

### Database connection details

Once you've set up the required driver, start Tableau and run through the
following steps:

1. On the left side, find the **Connect to a Server** section
1. Select **More** and then **PostgreSQL**
1. Use the following details to configure the connection:

    Field          | Value
    -------------- | ----------------------
    Server         | Materialize host name.
    Port           | **6875**
    Database       | **materialize**
    Authentication | Username and Password
    Username       | Materialize user.
    Password       | App-specific password.
    Require SSL    | ✓

4. Click **Sign In** to connect to Materialize

For more details and troubleshooting, check the
[Tableau documentation](https://help.tableau.com/current/pro/desktop/en-us/examples_postgresql.htm).

[//]: # "TODO(morsapaes) Clarify minimum refresh rate and details about live
connections"

## Configure a custom cluster

To direct queries to a specific cluster, [set the cluster at the role
level](/sql/alter-role) using the following SQL statement:

```sql
ALTER ROLE <your_user> SET CLUSTER = <custom_cluster>;
```

Replace `<your_user>` with the name of your Materialize role and `<custom_cluster>` with the name of the cluster you want to use.

Once set, all new sessions for that user will automatically run in the specified
cluster, eliminating the need to manually specify it in each query or
connection.

### Troubleshooting

Errors like the following indicate that the JDBC driver was not successfully
installed.

```
ERROR: Expected FOR, found WITH;
Error while executing the query
```

```
ERROR: WITH HOLD is unsupported for cursors;
Error while executing the query
```

The errors occur because Tableau falls back to a legacy PostgreSQL ODBC driver
that does not support connecting to Materialize. Follow the [Setup](#setup)
instructions again and ensure you've downloaded the driver to the correct folder
for your platform.

<!-- mz-docs page: serve-results/client-libraries -->

# Client libraries

Connect via client libraries/SQL drivers

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
| Python   | [`psycopg2`](https://pypi.org/project/psycopg2/)                | See the [Python cheatsheet](/serve-results/client-libraries/python/).   |
| Ruby     | [`pg` gem](https://rubygems.org/gems/pg/)                       | See the [Ruby cheatsheet](/serve-results/client-libraries/ruby/).       |
| Rust     | [`postgres-openssl`](https://crates.io/crates/postgres-openssl) | See the [Rust cheatsheet](/serve-results/client-libraries/rust/).       |

👋 _Is there another client library you'd like to use with Materialize? Submit a
[feature
request](https://github.com/MaterializeInc/materialize/discussions/new?category=feature-requests&labels=A-integration)._

<!-- mz-docs page: serve-results/client-libraries/golang -->

# Golang cheatsheet
Use Go to connect, insert, manage, query and stream from Materialize.
Materialize is **wire-compatible** with PostgreSQL, which means that Go applications can use the standard library's [`database/sql`](https://pkg.go.dev/database/sql) package with a PostgreSQL driver to interact with Materialize. In this guide, we'll use the [`pgx` driver](https://github.com/jackc/pgx) to connect to Materialize and issue SQL commands.

## Connect

To [connect](https://pkg.go.dev/github.com/jackc/pgx#ConnConfig) to Materialize using `pgx`, you can use either a URI or DSN [connection string](https://pkg.go.dev/github.com/jackc/pgx#ParseConnectionString):

```go
package main

import (
	"context"
	"github.com/jackc/pgx/v4"
	"log"
)

func main() {

	ctx := context.Background()
	connStr := "postgres://MATERIALIZE_USERNAME:APP_SPECIFIC_PASSWORD@MATERIALIZE_HOST:6875/materialize"

	conn, err := pgx.Connect(ctx, connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()
}
```

To create a concurrency-safe connection pool, import the [`pgxpool` package](https://pkg.go.dev/github.com/jackc/pgx/v4/pgxpool) and use `pgxpool.Connect`.

The remainder of this guide uses the [`*pgx.Conn`](https://pkg.go.dev/github.com/jackc/pgx#Conn) connection handle from the [connect](#connect) section to interact with Materialize.

## Create tables

Most data in Materialize will stream in via an external system, but a [table](/sql/create-table/) can be helpful for supplementary data. For example, you can use a table to join slower-moving reference or lookup data with a stream.

To create a table named `countries` in Materialize:

```go
createTableSQL := `
    CREATE TABLE IF NOT EXISTS countries (
        code CHAR(2),
        name TEXT
    );
`

_, err := conn.Exec(ctx, createTableSQL)
if err != nil {
    log.Fatal(err)
}
```

## Insert data into tables

To [insert a row](/sql/insert/) of data into a table named `countries` in Materialize:

```go
insertSQL := "INSERT INTO countries (code, name) VALUES ($1, $2)"

_, err := conn.Exec(ctx, insertSQL, "GH", "GHANA")
if err != nil {
    log.Fatal(err)
}
```

## Query

Querying Materialize is identical to querying a PostgreSQL database: Go executes the query, and Materialize returns the state of the view, source, or table at that point in time.

Because Materialize maintains results incrementally updated, response times are much faster than traditional database queries, and polling (repeatedly querying) a view doesn't impact performance.

To query the `countries` using a `SELECT` statement:

```go
rows, err := conn.Query(ctx, "SELECT * FROM countries")
if err != nil {
    log.Fatal(err)
}

for rows.Next() {
    var r result
    err = rows.Scan(&r...)
    if err != nil {
        log.Fatal(err)
    }
    // operate on result
}
```

## Manage sources, views, and indexes

Typically, you create sources, views, and indexes when deploying Materialize, but it's possible to use a Go app to execute common DDL statements.

### Create a source from Go

```go
createSourceSQL := `
    CREATE SOURCE IF NOT EXISTS auction
    FROM LOAD GENERATOR AUCTION FOR ALL TABLES;
`

_, err = conn.Exec(ctx, createSourceSQL)
if err != nil {
    log.Fatal(err)
}
```
For more information, see [`CREATE SOURCE`](/sql/create-source/).

### Create a view from Go

```go
createViewSQL := `
    CREATE MATERIALIZED VIEW IF NOT EXISTS amount_sum AS
        SELECT sum(amount)
    FROM bids;
`

_, err = conn.Exec(ctx, createViewSQL)
if err != nil {
    log.Fatal(err)
}
```

For more information, see [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/).

## Stream

To take full advantage of incrementally updated materialized views from a Go application, instead of [querying](#query) Materialize for the state of a view at a point in time, use a [`SUBSCRIBE` statement](/sql/subscribe/) to request a stream of updates as the view changes.

To read a stream of updates from an existing materialized view, open a long-lived transaction with `BEGIN` and use [`SUBSCRIBE` with `FETCH`](/sql/subscribe/#subscribing-with-fetch) to repeatedly fetch all changes to the view since the last query:

```go
tx, err := conn.Begin(ctx)
if err != nil {
    log.Fatal(err)
    return
}
defer tx.Rollback(ctx)

_, err = tx.Exec(ctx, "DECLARE c CURSOR FOR SUBSCRIBE amount_sum")
if err != nil {
    log.Fatal(err)
    return
}

for {
    rows, err := tx.Query(ctx, "FETCH ALL c")
    if err != nil {
        log.Fatal(err)
        tx.Rollback(ctx)
        return
    }

    for rows.Next() {
        var r subscribeResult
        if err := rows.Scan(&r.MzTimestamp, &r.MzDiff, ...); err != nil {
            log.Fatal(err)
        }
        fmt.Printf("%+v\n", r)
        // operate on subscribeResult
    }
}

err = tx.Commit(ctx)
if err != nil {
    log.Fatal(err)
}
```

The [SUBSCRIBE output format](/sql/subscribe/#output) of `subscribeResult` contains all of the columns of `amount_sum`, prepended with several additional columns that describe the nature of the update.  When a row of a subscribed view is **updated,** two objects will show up in the result set:

```go
{MzTimestamp:1646868332570 MzDiff:1 row...}
{MzTimestamp:1646868332570 MzDiff:-1 row...}
```

An `MzDiff` value of `-1` indicates that Materialize is deleting one row with the included values. An update is just a retraction (`MzDiff:-1`) and an insertion (`MzDiff:1`) with the same timestamp.

## Clean up

To clean up the sources, views, and tables that we created, first connect to Materialize using a [PostgreSQL client](/serve-results/sql-clients/) and then, run the following commands:

```mzsql
DROP MATERIALIZED VIEW IF EXISTS amount_sum;
DROP SOURCE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS countries;
```

## Go ORMs

ORM frameworks like **GORM** tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if a tool is compatible with PostgreSQL, it’s not guaranteed that the same integration will work out-of-the-box.

The level of support for these tools will improve as we extend the coverage of `pg_catalog` in Materialize and join efforts with each community to make the integrations Just Work™️.

<!-- mz-docs page: serve-results/client-libraries/java-jdbc -->

# Java cheatsheet
Use the PostgreSQL JDBC Driver to connect, insert, manage, query and stream from Materialize.
Materialize is **wire-compatible** with PostgreSQL, which means that Java
applications can use common PostgreSQL clients to interact with Materialize.
This guide uses the [PostgreSQL JDBC Driver](https://jdbc.postgresql.org/) to
connect to Materialize and issue SQL commands.

## Connect

To [connect](https://jdbc.postgresql.org/documentation/head/connect.html) to Materialize using the PostgreSQL JDBC Driver:

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

public class App {

    private final String url = "jdbc:postgresql://MATERIALIZE_HOST:6875/materialize";
    private final String user = "MATERIALIZE_USERNAME";
    private final String password = "MATERIALIZE_PASSWORD";

    /**
     * Connect to Materialize
     *
     * @return a Connection object
     */
    public Connection connect() {
        Properties props = new Properties();
        props.setProperty("user", user);
        props.setProperty("password", password);
        props.setProperty("ssl","true");
        Connection conn = null;
        try {
            conn = DriverManager.getConnection(url, props);
            System.out.println("Connected to Materialize successfully!");
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }

        return conn;
    }

    public static void main(String[] args) {
        App app = new App();
        app.connect();
    }
}
```

To establish the connection to Materialize, call the `getConnection()` method on the `DriverManager` class.

## Create tables

Most data in Materialize will stream in via an external system, but a [table](/sql/create-table/) can be helpful for supplementary data. For example, you can use a table to join slower-moving reference or lookup data with a stream.

To create a table named `countries` in Materialize:

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.PreparedStatement;

public class App {

    private final String url = "jdbc:postgresql://MATERIALIZE_HOST:6875/materialize";
    private final String user = "MATERIALIZE_USERNAME";
    private final String password = "MATERIALIZE_PASSWORD";

    /**
     * Connect to Materialize
     *
     * @return a Connection object
     */
    public Connection connect() throws SQLException {
        Properties props = new Properties();
        props.setProperty("user", user);
        props.setProperty("password", password);
        props.setProperty("ssl","true");

        return DriverManager.getConnection(url, props);

    }

    public void createTable() {

        String SQL = "CREATE TABLE IF NOT EXISTS countries (code CHAR(2), name TEXT)";

        try (Connection conn = connect()) {
            Statement st = conn.createStatement();
            st.execute(SQL);
            System.out.println("Table created.");
            st.close();
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    public static void main(String[] args) {
        App app = new App();
        app.createTable();
    }

}
```

## Insert data into tables

**Basic Example:** [Insert a row](/sql/insert/) of data into a table named `countries` in Materialize:

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.PreparedStatement;

public class App {

    private final String url = "jdbc:postgresql://MATERIALIZE_HOST:6875/materialize";
    private final String user = "MATERIALIZE_USERNAME";
    private final String password = "MATERIALIZE_PASSWORD";

    /**
     * Connect to Materialize
     *
     * @return a Connection object
     */
    public Connection connect() throws SQLException {
        Properties props = new Properties();
        props.setProperty("user", user);
        props.setProperty("password", password);
        props.setProperty("ssl","true");

        return DriverManager.getConnection(url, props);

    }

    public void insert() {

        try (Connection conn = connect()) {
            String code = "GH";
            String name = "Ghana";
            PreparedStatement st = conn.prepareStatement("INSERT INTO countries(code, name) VALUES(?, ?)");
            st.setString(1, code);
            st.setString(2, name);
            int rowsDeleted = st.executeUpdate();
            System.out.println(rowsDeleted + " rows inserted.");
            st.close();
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    public static void main(String[] args) {
        App app = new App();
        app.insert();
    }
}
```

## Query

Querying Materialize is identical to querying a PostgreSQL database: Java executes the query, and Materialize returns the state of the view, source, or table at that point in time.

Because Materialize keeps results incrementally updated, response times are much faster than traditional database queries, and polling (repeatedly querying) a view doesn't impact performance.

To query the `countries` using a `SELECT` statement:

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;
import java.sql.ResultSet;
import java.sql.Statement;

public class App {

    private final String url = "jdbc:postgresql://MATERIALIZE_HOST:6875/materialize";
    private final String user = "MATERIALIZE_USERNAME";
    private final String password = "MATERIALIZE_PASSWORD";

    /**
     * Connect to Materialize
     *
     * @return a Connection object
     */
    public Connection connect() throws SQLException {
        Properties props = new Properties();
        props.setProperty("user", user);
        props.setProperty("password", password);
        props.setProperty("ssl","true");

        return DriverManager.getConnection(url, props);

    }

    public void query() {

        String SQL = "SELECT * FROM countries";

        try (Connection conn = connect();
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(SQL)) {
            while (rs.next()) {
                System.out.println(rs.getString("code") + " " + rs.getString("name"));
            }
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    public static void main(String[] args) {
        App app = new App();
        app.query();
    }
}
```

For more details, see the [JDBC](https://jdbc.postgresql.org/documentation/head/query.html) documentation.

## Manage sources, views, and indexes

Typically, you create sources, views, and indexes when deploying Materialize, although it is possible to use a Java app to execute common DDL statements.

### Create a source from Java

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.PreparedStatement;

public class App {

    private final String url = "jdbc:postgresql://MATERIALIZE_HOST:6875/materialize";
    private final String user = "MATERIALIZE_USERNAME";
    private final String password = "MATERIALIZE_PASSWORD";

    /**
     * Connect to Materialize
     *
     * @return a Connection object
     */
    public Connection connect() throws SQLException {
        Properties props = new Properties();
        props.setProperty("user", user);
        props.setProperty("password", password);
        props.setProperty("ssl","true");

        return DriverManager.getConnection(url, props);

    }

    public void source() {

        String SQL = "CREATE SOURCE auction FROM LOAD GENERATOR AUCTION FOR ALL TABLES;";

        try (Connection conn = connect()) {
            Statement st = conn.createStatement();
            st.execute(SQL);
            System.out.println("Source created.");
            st.close();
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    public static void main(String[] args) {
        App app = new App();
        app.source();
    }
}
```

For more information, see [`CREATE SOURCE`](/sql/create-source/).

### Create a view from Java

```java
    public void view() {

        String SQL = "CREATE MATERIALIZED VIEW IF NOT EXISTS amount_sum AS "
                   + "SELECT sum(amount)"
                   + "FROM bids;";

        try (Connection conn = connect()) {
            Statement st = conn.createStatement();
            st.execute(SQL);
            System.out.println("View created.");
            st.close();
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }
```

For more information, see [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/).

## Stream

To take full advantage of incrementally updated materialized views from a Java application, instead of [querying](#query) Materialize for the state of a view at a point in time, use a [`SUBSCRIBE` statement](/sql/subscribe/) to request a stream of updates as the view changes.

To read a stream of updates from an existing materialized view, open a long-lived transaction with `BEGIN` and use [`SUBSCRIBE` with `FETCH`](/sql/subscribe/#subscribing-with-fetch) to repeatedly fetch all changes to the view since the last query:

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;
import java.sql.ResultSet;
import java.sql.Statement;

public class App {

    private final String url = "jdbc:postgresql://MATERIALIZE_HOST:6875/materialize";
    private final String user = "MATERIALIZE_USERNAME";
    private final String password = "MATERIALIZE_PASSWORD";

    /**
     * Connect to Materialize
     *
     * @return a Connection object
     */
    public Connection connect() throws SQLException {
        Properties props = new Properties();
        props.setProperty("user", user);
        props.setProperty("password", password);
        props.setProperty("ssl","true");

        return DriverManager.getConnection(url, props);

    }

    public void subscribe() {
        try (Connection conn = connect()) {

            Statement stmt = conn.createStatement();
            stmt.execute("BEGIN");
            stmt.execute("DECLARE c CURSOR FOR SUBSCRIBE amount_sum");
            while (true) {
                ResultSet rs = stmt.executeQuery("FETCH ALL c");
                if(rs.next()) {
                    System.out.println(rs.getString(1) + " " + rs.getString(2));
                }
            }
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    public static void main(String[] args) {
        App app = new App();
        app.subscribe();
    }
}
```

The [`SUBSCRIBE` output format](/sql/subscribe/#output) of `rs` is a `ResultSet` of view updates. When a row of a subscribed view is **updated,** two objects will show up in the `rows` array:

```java
    ...
    1648567756801 1 value_3
    1648567761801 1 value_4
    1648567785802 -1 value_4
    ...
```

A `mz_diff` value of `-1` indicates that Materialize is deleting one row with the included values.  An update is just a retraction (`mz_diff: '-1'`) and an insertion (`mz_diff: '1'`) with the same timestamp.

## Clean up

To clean up the sources, views, and tables that we created, first connect to Materialize using a [PostgreSQL client](/serve-results/sql-clients/) and then, run the following commands:

```mzsql
DROP MATERIALIZED VIEW IF EXISTS amount_sum;
DROP SOURCE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS countries;
```

## Java ORMs

ORM frameworks like **Hibernate** tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if a tool is compatible with PostgreSQL, it’s not guaranteed that the same integration will work out-of-the-box.

The level of support for these tools will improve as we extend the coverage of `pg_catalog` in Materialize and join efforts with each community to make the integrations Just Work™️.

<!-- mz-docs page: serve-results/client-libraries/node-js -->

# Node.js cheatsheet
Use Node.js to connect, insert, manage, query and stream from Materialize.
Materialize is **wire-compatible** with PostgreSQL, which means that Node.js applications can use common PostgreSQL clients to interact with Materialize. In this guide, we'll use the  [`node-postgres` library](https://node-postgres.com/) to connect to Materialize and issue SQL commands.

## Connect

To [connect](https://node-postgres.com/features/connecting) to Materialize using `node-postgres`, you can use the connection URI shorthand (`postgres://<USER>@<HOST>:<PORT>/<SCHEMA>`):

```js
const { Client } = require('pg');
const client = new Client({
    user: MATERIALIZE_USERNAME,
    password: MATERIALIZE_PASSWORD,
    host: MATERIALIZE_HOST,
    port: 6875,
    database: 'materialize',
    ssl: true
});

async function main() {
    await client.connect();
    /* Work with Materialize */
}

main();
```

## Create tables

Most data in Materialize will stream in via an external system, but a [table](/sql/create-table/) can be helpful for supplementary data. For example, you can use a table to join slower-moving reference or lookup data with a stream.

To create a table named `countries` in Materialize:

```js
const { Client } = require('pg');

const client = new Client({
    user: MATERIALIZE_USERNAME,
    password: MATERIALIZE_PASSWORD,
    host: MATERIALIZE_HOST,
    port: 6875,
    database: 'materialize',
    ssl: true
});

const createTableSQL = `
    CREATE TABLE IF NOT EXISTS countries (
        code CHAR(2),
        name TEXT
    );
`;

async function main() {
    await client.connect();
    const res = await client.query(createTableSQL);
    console.log(res);
}

main();
```

## Insert data into tables

**Basic Example:** [Insert a row](/sql/insert/) of data into a table named `countries` in Materialize:

```js
const { Client } = require('pg');

const client = new Client({
    user: MATERIALIZE_USERNAME,
    password: MATERIALIZE_PASSWORD,
    host: MATERIALIZE_HOST,
    port: 6875,
    database: 'materialize',
    ssl: true
});

const text = 'INSERT INTO countries(code, name) VALUES($1, $2);';
const values = ['GH', 'GHANA'];

async function main() {
    await client.connect();
    const res = await client.query(text, values);
    console.log(res);
}

main();
```

## Query

Querying Materialize is identical to querying a PostgreSQL database: Node.js executes the query, and Materialize returns the state of the view, source, or table at that point in time.

Because Materialize keeps results incrementally updated, response times are much faster than traditional database queries, and polling (repeatedly querying) a view doesn't impact performance.

To query the `countries` table:

```js
const { Client } = require('pg');

const client = new Client({
  user: MATERIALIZE_USERNAME,
  password: MATERIALIZE_PASSWORD,
  host: MATERIALIZE_HOST,
  port: 6875,
  database: 'materialize',
  ssl: true
});

async function main() {
  await client.connect();
  const res = await client.query('SELECT * FROM countries');
  console.log(res.rows);
};

main();
```

For more details, see the [`node-postgres` query](https://node-postgres.com/features/queries) and [pg.Result](https://node-postgres.com/api/result) documentation.

## Manage sources, views, and indexes

Typically, you create sources, views, and indexes when deploying Materialize, but it's also possible to use a Node.js app to execute common DDL statements.

### Create a source from Node.js

```js
const { Client } = require('pg');

const client = new Client({
    user: MATERIALIZE_USERNAME,
    password: MATERIALIZE_PASSWORD,
    host: MATERIALIZE_HOST,
    port: 6875,
    database: 'materialize',
    ssl: true
});

async function main() {
    await client.connect();
    const res = await client.query(
        `CREATE SOURCE auction FROM LOAD GENERATOR AUCTION FOR ALL TABLES;`
        );
    console.log(res);
}

main();
```

For more information, see [`CREATE SOURCE`](/sql/create-source/).

### Create a view from Node.js

```js
const { Client } = require('pg');

const client = new Client({
    user: MATERIALIZE_USERNAME,
    password: MATERIALIZE_PASSWORD,
    host: MATERIALIZE_HOST,
    port: 6875,
    database: "materialize",
    ssl: true,
});

async function main() {
    await client.connect();
    const res = await client.query(
        `CREATE MATERIALIZED VIEW IF NOT EXISTS amount_sum AS
            SELECT sum(amount)
        FROM bids;`
        );
    console.log(res);
}

main();
```

For more information, see [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/).

## Stream

To take full advantage of incrementally updated materialized views from a Node.js application, instead of [querying](#query) Materialize for the state of a view at a point in time, you can use a [`SUBSCRIBE` statement](/sql/subscribe/) to request a stream of updates as the view changes.

To read a stream of updates from an existing materialized view, open a long-lived transaction with `BEGIN` and use [`SUBSCRIBE` with `FETCH`](/sql/subscribe/#subscribing-with-fetch) to repeatedly fetch all changes to the view since the last query:

```js
const { Client } = require('pg');

async function main() {
  const client = new Client({
    user: MATERIALIZE_USERNAME,
    password: MATERIALIZE_PASSWORD,
    host: MATERIALIZE_HOST,
    port: 6875,
    database: "materialize",
    ssl: true,
  });
  await client.connect();

  await client.query('BEGIN');
  await client.query('DECLARE c CURSOR FOR SUBSCRIBE amount_sum WITH (SNAPSHOT = FALSE)');

  while (true) {
    const res = await client.query('FETCH ALL c');
    console.log(res.rows);
  }
}

main();
```

The [`SUBSCRIBE` output format](/sql/subscribe/#output) of `res.rows` is an array of view update objects. When a row of a subscribed view is **updated,** two objects will show up in the `rows` array:

```js
[
    ...
    {
        mz_timestamp: '1627225629000',
        mz_diff: '1',
        sum: 'value_1',
    },
    {
        mz_timestamp: '1627225629000',
        mz_diff: '-1',
        sum: 'value_2',
    },
    ...
]
```

An `mz_diff` value of `-1` indicates that Materialize is deleting one row with the included values. An update is just a retraction (`mz_diff: '-1'`) and an insertion (`mz_diff: '1'`) with the same timestamp.

<!--- NOT PUBLISHABLE UNTIL https://github.com/brianc/node-postgres/pull/2573 is merged
### Using pg-query-stream

```js
const { Client } = require('pg');
const QueryStream = require('pg-query-stream');

const client = new Client('postgres://materialize@localhost:6875/materialize');

client.connect((err, client) => {
  if (err) {
    throw err;
  }
  const stream = client.query(new QueryStream('SUBSCRIBE avg_bid', []));
  stream.pipe(process.stdout);
});
```
--->

## Clean up

To clean up the sources, views, and tables that we created, first connect to Materialize using a [PostgreSQL client](/serve-results/sql-clients/) and then, run the following commands:

```mzsql
DROP MATERIALIZED VIEW IF EXISTS amount_sum;
DROP SOURCE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS countries;
```

## Node.js ORMs

ORM frameworks like **Prisma**, **Sequelize**, or **TypeORM** tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if a tool is compatible with PostgreSQL, it’s not guaranteed that the same integration will work out-of-the-box.

The level of support for these tools will improve as we extend the coverage of `pg_catalog` in Materialize and join efforts with each community to make the integrations Just Work™️.

<!-- mz-docs page: serve-results/client-libraries/php -->

# PHP cheatsheet
Use PHP PDO to connect, insert, manage, query and stream from Materialize.
Materialize is **wire-compatible** with PostgreSQL, which means that PHP applications can use common PostgreSQL clients to interact with Materialize. In this guide, we'll use the [PDO_PGSQL driver](https://www.php.net/manual/en/ref.pdo-pgsql.php) to connect to Materialize and issue SQL commands.

## Connect

To [connect](https://www.php.net/manual/en/ref.pdo-pgsql.connection.php) to Materialize using `PDO_PGSQL`:

```php
<?php

function connect(string $host, int $port, string $db, string $user, string <password>): PDO
{
    try {
        <dsn> = "pgsql:host=$host;port=$port;dbname=$db;";

        // make a database connection
        return new PDO(
            <dsn>,
            $user,
            <password>,
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
        );
    } catch (PDOException $e) {
        die($e->getMessage());
    }
}

$connection = connect('MATERIALIZE_HOST', 6875, 'materialize', 'MATERIALIZE_USERNAME', 'MATERIALIZE_PASSWORD');
```

You can add the above code to a `config.php` file and then include it in your application with `require 'connect.php';`.

## Create tables

Most data in Materialize will stream in via an external system, but a [`TABLE` in Materialize](/sql/create-table/) can be helpful for supplementary data. For example, you can use a table to join slower-moving reference or lookup data with a stream.

To create a table named `countries` in Materialize:

```php
<?php
// Include the Postgres connection details
require 'connect.php';

$sql = 'CREATE TABLE IF NOT EXISTS countries (
    code CHAR(2),
    name TEXT
)';

$statement = $connection->prepare($sql);
$statement->execute();
```

## Insert data into tables

**Basic Example:** [Insert a row](/sql/insert/) of data into the `countries` table in Materialize.

```php
<?php
// Include the Postgres connection details
require 'connect.php';

$sql = 'INSERT INTO countries (name, code) VALUES (?, ?)';
$statement = $connection->prepare($sql);
$statement->execute(['United States', 'US']);
$statement->execute(['Canada', 'CA']);
$statement->execute(['Mexico', 'MX']);
$statement->execute(['Germany', 'DE']);

$countStmt = "SELECT COUNT(*) FROM countries";
$count = $connection->query($countStmt);
while (($row = $count->fetch(PDO::FETCH_ASSOC)) !== false) {
    var_dump($row);
}
```

## Query

Querying Materialize is identical to querying a PostgreSQL database: PHP executes the query, and Materialize returns the state of the view, source, or table at that point in time.

Because Materialize keeps results incrementally updated, response times are much faster than traditional database queries, and polling (repeatedly querying) a view doesn't impact performance.

To query the `countries` table using a `SELECT` statement:

```php
<?php
// Include the Postgres connection details
require 'connect.php';

$sql = 'SELECT * FROM countries';
$statement = $connection->query($sql);

while (($row = $statement->fetch(PDO::FETCH_ASSOC)) !== false) {
    var_dump($row);
}
```

For more details, see the [PHP `PDOStatement`](https://www.php.net/manual/en/pdostatement.fetch.php) documentation.

## Manage sources, views, and indexes

Typically, you create sources, views, and indexes when deploying Materialize, although it is possible to use a PHP app to execute common DDL statements.

### Create a source from PHP

```php
<?php
// Include the Postgres connection details
require 'connect.php';

$sql = "CREATE SOURCE auction FROM LOAD GENERATOR AUCTION FOR ALL TABLES;";

$statement = $connection->prepare($sql);
$statement->execute();

$sources = "SHOW SOURCES";
$statement = $connection->query($sources);
$result = $statement->fetchAll(PDO::FETCH_ASSOC);
var_dump($result);

```

For more information, see [`CREATE SOURCE`](/sql/create-source/).

### Create a view from PHP

```php
<?php
// Include the Postgres connection details
require 'connect.php';

$sql = "CREATE MATERIALIZED VIEW IF NOT EXISTS amount_sum AS SELECT SUM(amount) FROM bids;";

$statement = $connection->prepare($sql);
$statement->execute();

$views = "SHOW MATERIALIZED VIEWS";
$statement = $connection->query($views);
$result = $statement->fetchAll(PDO::FETCH_ASSOC);
var_dump($result);
```

For more information, see [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/).

## Stream

To take full advantage of incrementally updated materialized views from a PHP application, instead of [querying](#query) Materialize for the state of a view at a point in time, use a [`SUBSCRIBE` statement](/sql/subscribe/) to request a stream of updates as the view changes.

To read a stream of updates from an existing materialized view, open a long-lived transaction with `BEGIN` and use [`SUBSCRIBE` with `FETCH`](/sql/subscribe/#subscribing-with-fetch) to repeatedly fetch all changes to the view since the last query:

```php
<?php
// Include the Postgres connection details
require 'connect.php';

// Begin a transaction
$connection->beginTransaction();
// Declare a cursor
$statement = $connection->prepare('DECLARE c CURSOR FOR SUBSCRIBE amount_sum WITH (FETCH = true);');
// Execute the statement
$statement->execute();

/* Fetch all of the remaining rows in the result set */
while (true) {
    //$result = $statement->fetchAll();
    $subscribe = $connection->prepare('FETCH ALL c');
    $subscribe->execute();
    $result = $subscribe->fetchAll(PDO::FETCH_ASSOC);
    print_r($result);
}
```

The [SUBSCRIBE output format](/sql/subscribe/#output) of `result` is an array of view updates objects. When a row of a subscribed view is **updated,** two objects will show up in the `result` array:

```php
    ...
        Array
        (
            [0] => Array
                (
                    [mz_timestamp] => 1646310999683
                    [mz_diff] => 1
                    [sum] => 'value_1'
                )

        )
        Array
        (
            [0] => Array
                (
                    [mz_timestamp] => 1646311002682
                    [mz_diff] => -1
                    [sum] => 'value_2'
                )

        )
    ...
```

An `mz_diff` value of `-1` indicates Materialize is deleting one row with the included values.  An update is just a retraction (`mz_diff: '-1'`) and an insertion (`mz_diff: '1'`) with the same timestamp.

## Clean up

To clean up the sources, views, and tables that we created, first connect to Materialize using a [PostgreSQL client](/serve-results/sql-clients/) and then, run the following commands:

```mzsql
DROP MATERIALIZED VIEW IF EXISTS ammount_sum;
DROP SOURCE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS countries;
```

## PHP ORMs

ORM frameworks like **Eloquent** tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if a tool is compatible with PostgreSQL, it’s not guaranteed that the same integration will work out-of-the-box.

The level of support for these tools will improve as we extend the coverage of `pg_catalog` in Materialize and join efforts with each community to make the integrations Just Work™️.

<!-- mz-docs page: serve-results/client-libraries/python -->

# Python cheatsheet
Use Python to connect, insert, manage, query and stream from Materialize.
Materialize is **wire-compatible** with PostgreSQL, which means that Python applications can use common PostgreSQL clients to interact with Materialize. In this guide, we'll use the [`psycopg2`](https://pypi.org/project/psycopg2/) adapter to connect to Materialize and issue SQL commands.

## Connect

To [connect](https://www.psycopg.org/docs/usage.html) to a local Materialize instance using `psycopg2`:

```python
#!/usr/bin/env python3

import psycopg2
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg2.connect(dsn)
```

## Create tables

Most data in Materialize will stream in via an external system, but a [table](/sql/create-table/) can be helpful for supplementary data. For example, use a table to join slower-moving reference or lookup data with a stream.

To create a table named `countries` in Materialize:

```python
#!/usr/bin/env python3

import psycopg2
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg2.connect(dsn)

with conn.cursor() as cur:
    cur.execute("CREATE TABLE IF NOT EXISTS countries (code CHAR(2), name TEXT);")

with conn.cursor() as cur:
    cur.execute("SHOW TABLES")
    print(cur.fetchone())
```

## Insert data into tables

**Basic Example:** [Insert a row](/sql/insert/) of data into a table named `countries` in Materialize.

```python
#!/usr/bin/env python3

import psycopg2
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg2.connect(dsn)

cur = conn.cursor()
cur.execute("INSERT INTO countries (name, code) VALUES (%s, %s)", ('United States', 'US'))
cur.execute("INSERT INTO countries (name, code) VALUES (%s, %s)", ('Canada', 'CA'))
cur.execute("INSERT INTO countries (name, code) VALUES (%s, %s)", ('Mexico', 'MX'))
cur.execute("INSERT INTO countries (name, code) VALUES (%s, %s)", ('Germany', 'DE'))
conn.commit()
cur.close()

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM countries;")
    print(cur.fetchone())

conn.close()
```

## Query

Querying Materialize is identical to querying a PostgreSQL database: Python executes the query, and Materialize returns the state of the view, source, or table at that point in time.

Because Materialize keeps results incrementally updated, response times are much faster than traditional database queries, and polling (repeatedly querying) a view doesn't impact performance.

To query the `countries` table using a `SELECT` statement:

```python
#!/usr/bin/env python3

import psycopg2
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg2.connect(dsn)

with conn.cursor() as cur:
    cur.execute("SELECT * FROM countries;")
    for row in cur:
        print(row)
```

For more details, see the [Psycopg](https://www.psycopg.org/docs/usage.html) documentation.

## Manage sources, views, and indexes

Typically, you create sources, views, and indexes when deploying Materialize, although it is possible to use a Python app to execute common DDL statements.

### Create a source from Python

```python
#!/usr/bin/env python3

import psycopg2
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg2.connect(dsn)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute("CREATE SOURCE auction FROM LOAD GENERATOR AUCTION FOR ALL TABLES;")

with conn.cursor() as cur:
    cur.execute("SHOW SOURCES")
    print(cur.fetchone())
```

For more information, see [`CREATE SOURCE`](/sql/create-source/).

### Create a view from Python

```python
#!/usr/bin/env python3

import psycopg2
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg2.connect(dsn)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute("CREATE MATERIALIZED VIEW IF NOT EXISTS amount_sum AS " \
            "SELECT sum(amount)" \
            "FROM bids;")

with conn.cursor() as cur:
    cur.execute("SHOW VIEWS")
    print(cur.fetchone())
```

For more information, see [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/).

## Stream

To take full advantage of incrementally updated materialized views from a Python application, instead of [querying](#query) Materialize for the state of a view at a point in time, use a [`SUBSCRIBE` statement](/sql/subscribe/) to request a stream of updates as the view changes.

To read a stream of updates from an existing materialized view, open a long-lived transaction with `BEGIN` and use [`SUBSCRIBE` with `FETCH`](/sql/subscribe/#subscribing-with-fetch) to repeatedly fetch all changes to the view since the last query:

```python
#!/usr/bin/env python3

import psycopg2
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg2.connect(dsn)

with conn.cursor() as cur:
    cur.execute("DECLARE c CURSOR FOR SUBSCRIBE amount_sum")
    while True:
        cur.execute("FETCH ALL c")
        for row in cur:
            print(row)
```

The [SUBSCRIBE output format](/sql/subscribe/#output) of `cur` is a data access object that can be used to iterate over the set of rows. When a row of a subscribed view is **updated,** two objects will show up in the `rows` array:

```python
    ...
(Decimal('1648737001490'), 1, 'my_value_1')
(Decimal('1648737001490'), 1, 'my_value_2')
(Decimal('1648737001490'), 1, 'my_value_3')
(Decimal('1648737065479'), -1, 'my_value_3')
(Decimal('1648737065479'), 1, 'my_value_4')
    ...
```

A `mz_diff` value of `-1` indicates Materialize is deleting one row with the included values.  An update is just a retraction (`mz_diff: '-1'`) and an insertion (`mz_diff: '1'`) with the same timestamp.

### Streaming with `psycopg3`

Although `psycopg3` can function identically as the `psycopg2` example above,
it provides a `stream` feature where rows are not buffered, which allows you to use `SUBSCRIBE` directly:

```python
#!/usr/bin/env python3

import psycopg
import sys

dsn = "user=MATERIALIZE_USERNAME password=MATERIALIZE_PASSWORD host=MATERIALIZE_HOST port=6875 dbname=materialize sslmode=require"
conn = psycopg.connect(dsn)

with conn.cursor() as cur:
    for row in cur.stream("SUBSCRIBE amount_sum"):
        print(row)
```

## Clean up

To clean up the sources, views, and tables that we created, first connect to Materialize using a [PostgreSQL client](/serve-results/sql-clients/) and then, run the following commands:

```mzsql
DROP MATERIALIZED VIEW IF EXISTS amount_sum;
DROP SOURCE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS countries;
```

## Python ORMs

ORM frameworks tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if a tool is compatible with PostgreSQL, it’s not guaranteed that the same integration will work out-of-the-box.

The level of support for these tools will improve as we extend the coverage of `pg_catalog` in Materialize and join efforts with each community to make the integrations Just Work™️.

Check out the [integrations page](/developer-tools/integrations/) for a list of ORM frameworks
that are known to work well with Materialize.

<!-- mz-docs page: serve-results/client-libraries/ruby -->

# Ruby cheatsheet
Use Ruby to connect, insert, manage, query and stream from Materialize.
Materialize is **wire-compatible** with PostgreSQL, which means that Ruby applications can use common PostgreSQL clients to interact with Materialize. In this guide, we'll use the  [`pg` gem](https://rubygems.org/gems/pg/) to connect to Materialize and issue SQL commands.

## Connect

To connect to Materialize using `pg`:

```ruby
require 'pg'

conn = PG.connect(host:"MATERIALIZE_HOST", port: 6875, user: "MATERIALIZE_USERNAME", password: "MATERIALIZE_PASSWORD")
```

If you don't have a `pg` gem, you can install it with:

```bash
gem install pg
```

## Create tables

Most data in Materialize will stream in via an external system, but a [table](/sql/create-table/) can be helpful for supplementary data. For example, you can use a table to join slower-moving reference or lookup data with a stream.

To create a table named `countries` in Materialize:

```ruby
require 'pg'

conn = PG.connect(host:"MATERIALIZE_HOST", port: 6875, user: "MATERIALIZE_USERNAME", password: "MATERIALIZE_PASSWORD")

conn.exec("CREATE TABLE IF NOT EXISTS countries (code CHAR(2), name TEXT);")

res  = conn.exec('SHOW TABLES')

res.each do |row|
  puts row
end
```

## Insert data into tables

**Basic Example:** [Insert a row](/sql/insert/) of data into a table named `countries` in Materialize:

```ruby
require 'pg'

conn = PG.connect(host:"MATERIALIZE_HOST", port: 6875, user: "MATERIALIZE_USERNAME", password: "MATERIALIZE_PASSWORD")

conn.exec("INSERT INTO countries (code, name) VALUES ('US', 'United States');")
conn.exec("INSERT INTO countries (code, name) VALUES ('CA', 'Canada');")

res  = conn.exec('SELECT * FROM countries')

res.each do |row|
  puts row
end
```

## Query

Querying Materialize is identical to querying a PostgreSQL database: Ruby executes the query, and Materialize returns the state of the view, source, or table at that point in time.

Because Materialize keeps results incrementally updated, response times are much faster than traditional database queries, and polling (repeatedly querying) a view doesn't impact performance.

To query the `countries` table using a `SELECT` statement:

```ruby
require 'pg'

conn = PG.connect(host:"MATERIALIZE_HOST", port: 6875, user: "MATERIALIZE_USERNAME", password: "MATERIALIZE_PASSWORD")

res  = conn.exec('SELECT * FROM countries')

res.each do |row|
  puts row
end
```

For more details, see the [`exec` instance method](https://rubydoc.info/gems/pg/0.10.0/PGconn#exec-instance_method) documentation.

## Manage sources, views, and indexes

Typically, you create sources, views, and indexes when deploying Materialize, but it's also possible to use a Ruby app to execute common DDL statements.

### Create a source from Ruby

```ruby
require 'pg'

conn = PG.connect(host:"MATERIALIZE_HOST", port: 6875, user: "MATERIALIZE_USERNAME", password: "MATERIALIZE_PASSWORD")

# Create a source
src = conn.exec(
    "CREATE SOURCE IF NOT EXISTS auction FROM LOAD GENERATOR AUCTION FOR ALL TABLES;"
);

puts src.inspect

# Show the source
res = conn.exec("SHOW SOURCES")
res.each do |row|
  puts row
end
```

For more information, see [`CREATE SOURCE`](/sql/create-source/).

### Create a view from Ruby

```ruby
require 'pg'

conn = PG.connect(host:"MATERIALIZE_HOST", port: 6875, user: "MATERIALIZE_USERNAME", password: "MATERIALIZE_PASSWORD")

# Create a view
view = conn.exec(
    "CREATE MATERIALIZED VIEW IF NOT EXISTS amount_sum AS
      SELECT sum(amount)
    FROM bids;"
);
puts view.inspect

# Show the view
res = conn.exec("SHOW MATERIALIZED VIEWS")
res.each do |row|
  puts row
end
```

For more information, see [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/).

## Stream

To take full advantage of incrementally updated materialized views from a Ruby application, instead of [querying](#query) Materialize for the state of a view at a point in time, use a [`SUBSCRIBE` statement](/sql/subscribe/) to request a stream of updates as the view changes.

To read a stream of updates from an existing materialized view, open a long-lived transaction with `BEGIN` and use [`SUBSCRIBE` with `FETCH`](/sql/subscribe/#subscribing-with-fetch) to repeatedly fetch all changes to the view since the last query:

```ruby
require 'pg'

# Locally running instance:
conn = PG.connect(host:"MATERIALIZE_HOST", port: 6875, user: "MATERIALIZE_USERNAME", password: "MATERIALIZE_PASSWORD")
conn.exec('BEGIN')
conn.exec('DECLARE c CURSOR FOR SUBSCRIBE amount_sum')

while true
  conn.exec('FETCH c') do |result|
    result.each do |row|
      puts row
    end
  end
end
```

Each `result` of the [SUBSCRIBE output format](/sql/subscribe/#output) has exactly object. When a row of a subscribed view is **updated,** two objects will show up:

```json
...
{"mz_timestamp"=>"1648126887708", "mz_diff"=>"1", "sum"=>"1"}
{"mz_timestamp"=>"1648126887708", "mz_diff"=>"1", "sum"=>"2"}
{"mz_timestamp"=>"1648126887708", "mz_diff"=>"1", "sum"=>"3"}
{"mz_timestamp"=>"1648126897364", "mz_diff"=>"-1", "sum"=>"1"}
...
```

An `mz_diff` value of `-1` indicates Materialize is deleting one row with the included values.  An update is just a retraction (`mz_diff: '-1'`) and an insertion (`mz_diff: '1'`) with the same `mz_timestamp`.

## Clean up

To clean up the sources, views, and tables that we created, first connect to Materialize using a [PostgreSQL client](/serve-results/sql-clients/) and then, run the following commands:

```mzsql
DROP MATERIALIZED VIEW IF EXISTS amount_sum;
DROP SOURCE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS countries;
```

## Ruby ORMs

ORM frameworks like **Active Record** tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if a tool is compatible with PostgreSQL, it’s not guaranteed that the same integration will work out-of-the-box.

The level of support for these tools will improve as we extend the coverage of `pg_catalog` in Materialize and join efforts with each community to make the integrations Just Work™️.

<!-- mz-docs page: serve-results/client-libraries/rust -->

# Rust cheatsheet
Use Rust postgres-openssl to connect, insert, manage, query and stream from Materialize.
Materialize is **wire-compatible** with PostgreSQL, which means that Rust applications can use common PostgreSQL clients to interact with Materialize. In this guide, we'll use the [`postgres-openssl`](https://docs.rs/postgres-openssl/latest/postgres_openssl/) crate (the TLS support for [`tokio-postgres`](https://crates.io/crates/tokio-postgres) via `openssl`) to connect to Materialize and issue SQL commands.

## Connect

To connect to Materialize using `postgres-openssl`:

```rust
use openssl::ssl::{SslConnector, SslMethod, SslVerifyMode};
use postgres::{Client, Error};
use postgres_openssl::MakeTlsConnector;

pub(crate) fn create_client() -> Result<Client, Error> {
    let mut builder = SslConnector::builder(SslMethod::tls()).expect("Error creating builder.");
    builder.set_verify(SslVerifyMode::NONE);
    let connector = MakeTlsConnector::new(builder.build());

    let config = "postgres://MATERIALIZE_USERNAME:APP_SPECIFIC_PASSWORD@MATERIALIZE_HOST:6875/materialize?sslmode=require";
    Client::connect(config, connector)
}
```

## Create tables

Most data in Materialize will stream in via an external system, but a [table](/sql/create-table/) can be helpful for supplementary data. For example, you can use a table to join slower-moving reference or lookup data with a stream.

To create a table named `countries` in Materialize:

```rust
use postgres::Error;

use crate::connection::create_client;

pub(crate) fn create_table() -> Result<u64, Error> {
    let mut client = create_client().expect("Error creating client.");

    client.execute(
        "
        CREATE TABLE IF NOT EXISTS countries (
            code CHAR(2),
            name TEXT
        );
    ",
        &[],
    )
}
```

## Insert data into tables

To [insert a row](/sql/insert/) of data into a table named `countries` in Materialize:

```rust
use postgres::Error;

use crate::connection::create_client;

pub(crate) fn insert() -> Result<u64, Error> {
    let mut client = create_client().expect("Error creating client.");

    let code = "GH";
    let name = "Ghana";

    client.execute(
        "INSERT INTO countries(code, name) VALUES($1, $2)",
        &[&code, &name],
    )
}
```

## Query

Querying Materialize is identical to querying a PostgreSQL database. Here's how to do a SELECT statement:

```rust
use crate::connection::create_client;

pub(crate) fn run_query () {
    let mut client = create_client().expect("Error creating client.");

    let results = client.query("SELECT code, name FROM countries;", &[]).expect("Error running query.");

    for row in results {
        println!("{:} - {:}", row.get::<usize, String>(0), row.get::<usize, String>(1));
    };
}
```

## Manage sources, views, and indexes

Typically, you create sources, views, and indexes when deploying Materialize, although it is possible to use a Rust app to execute common DDL statements.

### Create a source from Rust

```rust
use postgres::Error;

use crate::connection::create_client;

pub(crate) fn create_source() -> Result<u64, Error> {
    let mut client = create_client().expect("Error creating client.");

    client.execute(
        "
        CREATE SOURCE IF NOT EXISTS auction
        FROM LOAD GENERATOR AUCTION FOR ALL TABLES;
    ",
        &[],
    )
}
```

### Create a view from Rust

```rust
use postgres::Error;

use crate::connection::create_client;

pub(crate) fn create_materialized_view() -> Result<u64, Error> {
    let mut client = create_client().expect("Error creating client.");

    client.execute(
        "
        CREATE MATERIALIZED VIEW IF NOT EXISTS amount_sum AS
        SELECT sum(amount)
        FROM bids;
    ",
        &[],
    )
}
```

## Stream

Materialize is designed to stream changes to views. To subscribe to a stream of updates in Rust, you can use the `SUBSCRIBE` feature. Here's how to subscribe to a stream:

```rust
use crate::connection::create_client;

pub(crate) fn subscribe() {
    let mut client = create_client().expect("Error creating client.");
    let mut transaction = client.transaction().expect("Error creating transaction.");
    transaction.execute("DECLARE c CURSOR FOR SUBSCRIBE (SELECT sum::text FROM amount_sum) WITH (SNAPSHOT = false);", &[]).expect("Error creating cursor.");

    loop {
        let results = transaction.query("FETCH ALL c;", &[]).expect("Error running fetch.");
        for row in results {
            println!("{:}", row.get::<usize, String>(2));
        }
    }
}
```

The [SUBSCRIBE output format](/sql/subscribe/#output) of the `amount_sum` view contains all of the columns of the view, prepended with several additional columns that describe the nature of the update.

## Clean up

To clean up the sources, views, and tables that we created, first connect to Materialize using a [PostgreSQL client](/serve-results/sql-clients/) and then, run the following commands:

```mzsql
DROP MATERIALIZED VIEW IF EXISTS amount_sum;
DROP SOURCE IF EXISTS auction CASCADE;
DROP TABLE IF EXISTS countries;
```

## ORM

Rust ORMs like `Diesel` and `sqlx` tend to run complex introspection queries that may use configuration settings, system tables or features not yet implemented in Materialize. This means that even if a tool is compatible with PostgreSQL, it’s not guaranteed that the same integration will work out-of-the-box.

The level of support for these tools will improve as we extend the coverage of `pg_catalog` in Materialize and join efforts with each community to make the integrations Just Work™️.

<!-- mz-docs page: serve-results/connection-pooling -->

# Connection Pooling
How to use connection pooling with Materialize
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

<!-- mz-docs page: serve-results/durable-subscriptions -->

# Durable subscriptions
How to enable lossless, durable subscriptions to your changing results in Materialize
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

<!-- mz-docs page: serve-results/fdw -->

# Use foreign data wrapper (FDW)
Use FDW to query results from Materialize
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

<!-- mz-docs page: serve-results/fdw-setup -->

# Foreign data wrapper (FDW) 
Use FDW to access Materialize
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

<!-- mz-docs page: serve-results/http-api -->

# Connect to Materialize via HTTP
How to use Materialize via HTTP
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

<!-- mz-docs page: serve-results/isolation-level -->

# Isolation levels
Materialize supports different isolation levels that determine how it isolates the execution of transactions.
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

<!-- mz-docs page: serve-results/query-results -->

# `SELECT` and `SUBSCRIBE`
Querying results from Materialize using `SELECT` and `SUBSCRIBE`.
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


<!-- mz-docs page: serve-results/sql-clients -->

# SQL clients
How to connect to Materialize using common SQL clients
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

<!-- mz-docs page: serve-results/troubleshooting -->

# Troubleshooting
How to troubleshoot common data transformation scenarios where Materialize is not working as expected.
Once data is flowing into Materialize and you start modeling it in SQL, you
might run into some snags or unexpected scenarios. This guide collects common
questions around data transformation to help you troubleshoot your queries.

## Why is my query slow?

<!-- TODO: update this to use the query history UI once it's available -->
The most common reasons for query execution taking longer than expected are:

* Processing lag in upstream dependencies, like materialized views and indexes
* Index design
* Query design

Each of these reasons requires a different approach for troubleshooting. Follow
the guidance below to first detect the source of slowness, and then address it
accordingly.

### Lagging materialized views or indexes

#### Detect

When a materialized view or index upstream of your query is behind on
processing, your query must wait for it to catch up before returning results.
This is how Materialize ensures consistent results for all queries.

To check if any materialized views or indexes are lagging, use the workflow
graphs in the Materialize console.

1. Go to https://console.materialize.com/.
2. Click on the **"Clusters"** tab in the side navigation bar.
3. Click on the cluster that contains your upstream materialized view or index.
4. Go to the **"Materialized Views"** or **"Indexes"** section, and click on the
object name to access its workflow graph.

If you find that one of the upstream materialized views or indexes is lagging,
this could be the cause of your query slowness.

#### Address

To troubleshoot and fix a lagging materialized view or index, follow the steps
in the [dataflow troubleshooting](/transform-data/dataflow-troubleshooting) guide.

*Do you have multiple materialized views chained on top of each other? Are you
seeing small amounts of lag?*<br>
Tip: avoid intermediary materialized views where not necessary. Each chained
materialized view incurs a small amount of processing lag from the previous
one.
<!-- TODO add more guidance on avoiding chained mat views-->

Other options to consider:

* If you've gone through the dataflow troubleshooting and do not want to make
  any changes to your query, consider [sizing up your cluster](/sql/create-cluster/#available-sizes).
* You can also consider changing your [isolation level](/serve-results/isolation-level/),
  depending on the consistency guarantees that you need. With a lower isolation
  level, you may be able to query stale results out of lagging indexes and
  materialized views.
* You can also check whether you're using a [transaction](#transactions) and
  follow the guidance there.

### Slow query execution

Query execution time largely depends on the amount of on-the-fly work that needs
to be done to compute the result. You can cut back on execution time in a few
ways:

#### Indexing and query optimization

Like in any other database, index design affects query performance. If the
dependencies of your query don't have [indexes](/sql/create-index/) defined,
you should consider creating one (or many). Check out the [optimization guide](/transform-data/optimization)
for guidance on how to optimize query performance. For information on when
to use a materialized view versus an index, check out the
[materialized view reference documentation](/sql/create-materialized-view/#details) .

If the dependencies of your query are indexed, you should confirm that the query
is actually using the index! This information is available in the query plan,
which you can view using the [`EXPLAIN PLAN`](/sql/explain-plan/) command. If
you run `EXPLAIN PLAN` for your query and see the index(es) under `Used indexes`,
this means that the index was correctly used. If that's not the case, consider:

* Are you running the query in the same cluster which contains the index? You
  must do so in order for the index to be used.
* Does the index's indexed expression (key) match up with how you're querying
  the data?

#### Result filtering

If you are just looking to validate data and don't want to deal with query
optimization at this stage, you can improve the efficiency of validation
queries by reducing the amount of data that Materialize needs to read. You can
achieve this by adding `LIMIT` clauses or [temporal filters](/transform-data/patterns/temporal-filters/)
to your queries.

**`LIMIT` clause**

Use the standard `LIMIT` clause to return at most the specified number of rows.
It's important to note that this only applies to basic queries against **a
single** source, materialized view or table, with no ordering, filters or
offsets.

```mzsql
SELECT <column list or *>
FROM <source, materialized view or table>
LIMIT <25 or less>;
```

To verify whether the query will return quickly, use [`EXPLAIN PLAN`](/sql/explain-plan/)
to get the execution plan for the query, and validate that it starts with
`Explained Query (fast path)`.

**Temporal filters**

Use temporal flters to filter results on a timestamp column that correlates with
the insertion or update time of each row. For example:

```mzsql
WHERE mz_now() <= event_ts + INTERVAL '1hr'
```

Materialize is able to “push down” temporal filters all the way down to its
storage layer, skipping over old data that isn't relevant to the query. For
more details on temporal filter pushdown, see the [reference documentation](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Other things to consider

#### Transactions
<!-- Copied from doc/user/content/manage/troubleshooting.md#Transactions -->
Transactions are a database concept for bundling multiple query steps into a
single, all-or-nothing operation. You can read more about them in the
[transactions](/sql/begin) section of our docs.

In Materialize, `BEGIN` starts a transaction block. All statements in a
transaction block will be executed in a single transaction until an explicit
`COMMIT` or `ROLLBACK` is given. All statements in that transaction happen at
the same timestamp, and that timestamp must be valid for all objects the
transaction may access.

What this means for latency: Materialize may delay queries against "slow"
tables, materialized views, and indexes until they catch up to faster ones in
the same schema. We recommend you avoid using transactions in contexts where
you require low latency responses and are not certain that all objects in a
schema will be equally current.

What you can do:

- Avoid using transactions where you don’t need them. For example, if you’re
  only executing single statements at a time.
- Double check whether your SQL library or ORM is wrapping all queries in
  transactions on your behalf, and disable that setting, only using
  transactions explicitly when you want them.

#### Client-side latency
<!-- Copied from doc/user/content/manage/troubleshooting.md#client-side-latency -->
To minimize the roundtrip latency associated with making requests from your
client to Materialize, make your requests as physically close to your
Materialize region as possible. For example, if you use the AWS `us-east-1`
region for Materialize, your client server would ideally also be running in AWS
`us-east-1`.

#### Result size
<!-- TODO: Use the query history UI to fetch result size -->
Smaller results lead to less time spent transmitting data over the network. You
can calculate your result size as `number of rows returned x byte size of each
row`, where `byte size of each row = sum(byte size of each column)`. If your
result size is large, this will be a factor in query latency.

#### Cluster CPU
Another thing to check is how busy the cluster you're issuing queries on is. A
busy cluster means your query might be blocked by some other processing going
on, taking longer to return. As an example, if you issue a lot of
resource-intensive queries at once, that might spike the CPU.

The measure of cluster busyness is CPU. You can monitor CPU usage in the
[Materialize console](/developer-tools/console/) by clicking
the **"Clusters"** tab in the navigation bar, and clicking into the cluster.
You can also grab CPU usage from the system catalog using SQL:

```mzsql
SELECT cru.cpu_percent
FROM mz_internal.mz_cluster_replica_utilization cru
LEFT JOIN mz_catalog.mz_cluster_replicas cr ON cru.replica_id = cr.id
LEFT JOIN mz_catalog.mz_clusters c ON cr.cluster_id = c.id
WHERE c.name = <CLUSTER_NAME>;
```

## Why is my query not responding?

The most common reasons for query hanging are:

* An upstream source is stalled
* An upstream source is still snapshotting
* An upstream object is still hydrating
* Your cluster is unhealthy

Each of these reasons requires a different approach for troubleshooting. Follow
the guidance below to first detect the source of the hang, and then address it
accordingly.

> **Note:** Your query may be running, just slowly. If none of the reasons below detects
> your issue, jump to [Why is my query slow?](#why-is-my-query-slow) for further
> guidance.

### Stalled source

<!-- TODO: update this to use the query history UI once it's available -->
To detect and address stalled sources, follow the [`Ingest data` troubleshooting](/ingest-data/troubleshooting)
guide.

### Snapshotting source

When a source is created, it must first _snapshot_ the existing data from the
upstream system before it can serve results. That is, queries that depend on a
source that is snapshotting **block until the snapshot is complete**.

Unlike hydration, snapshotting reads from the upstream system. For large upsert
sources, this process can be resource-intensive and take a long time. For help
on diagnosing a slow snapshot and sizing a cluster appropriately for
snapshotting, follow the [`Ingest data`
troubleshooting](/ingest-data/troubleshooting) guide.

For upsert sources, see also [Hydrating objects](#hydrating-objects).

### Hydrating objects

Queries that depend on objects that are hydrating **block until hydration is
complete**. _Hydration_ is when Materialize reconstructs the in-memory state of
an object by reading from its storage layer (not from the upstream system).
Hydration time is proportional to data volume and query complexity. This means
that you should expect objects with large volumes of data and/or complex queries
to take longer to hydrate.

When a materialized view or index is created, it undergoes hydration. Hydration
also happens whenever a cluster is restarted or resized: the materialized views
and indexes on that cluster rebuild their in-memory state, and upsert sources
rebuild their internal index. On Materialize Cloud, this includes restarts
during the [routine maintenance
window](/releases/schedule/#cloud-upgrade-schedule).

To see whether an object is still hydrating, navigate to the
[workflow graph](#detect) for the object in the Materialize console.

### Unhealthy cluster

#### Detect

If your cluster replica reaches its capacity (i.e., it OOMs at 100% Memory Utilization), this will result in a crash. After a crash, the cluster replica has to restart, which can take a few seconds. On cluster restart, your query will also automatically restart execution from the beginning.

If your cluster replica is CPU-maxed out (~100% CPU usage), your query may be blocked while the cluster processes the other activity. It may eventually complete, but it will continue to be slow and potentially blocked until the CPU usage goes down. As an example, if you issue a lot of resource-intensive queries at once, that might spike the CPU.

We recommend setting [Alerting thresholds](https://materialize.com/docs/manage/monitor/alerting/#thresholds) to notify your team when a cluster is reaching its capacity. Please note that these are recommendations, and some configurations may reach unstable memory utilization levels sooner than the thresholds.

To see Memory Utilization and CPU usage for your cluster replica in the [Materialize console](https://materialize.com/docs/developer-tools/console/clusters/), go to [https://console.materialize.com/](/developer-tools/console/), click the **“Clusters”** tab in the navigation bar, and click on the cluster name.

#### Address

Your query may have been the root cause of the increased Memory Utilization and CPU usage, or it may have been something else happening on the cluster at the same time. To troubleshoot and fix Memory Utilization and CPU usage, follow the steps in the [dataflow troubleshooting](https://materialize.com/docs/transform-data/dataflow-troubleshooting) guide.

For guidance on how to reduce Memory Utilization and CPU usage for this or another query, take a look at the [indexing and query optimization](https://materialize.com/docs/serve-results/troubleshooting/#indexing-and-query-optimization) and result filtering sections above.

If your query was the root cause, you’ll need to kill it for the cluster replica’s Memory Utilization or CPU to go down. If your query was causing an OOM, the cluster replica will continue to be in an “OOM loop” - every time the replica restarts, the query restarts executing automatically then causes an OOM again - until you kill the query.

If your query was not the root cause, you can wait for the other activity on the cluster to stop and Memory Utilization/CPU to go down, or switch to a different cluster.

If you’ve gone through the dataflow troubleshooting and do not want to make any changes to your query, consider [sizing up your cluster](https://materialize.com/docs/sql/create-cluster/#available-sizes). A larger size cluster will provision more resources.

## Which part of my query runs slowly or uses a lot of memory?

You can [`EXPLAIN`](/sql/explain-plan/) a query to see how it will be run as a
dataflow. In particular, `EXPLAIN PHYSICAL PLAN` (the default) will show the concrete, fully
optimized plan that Materialize will run. That plan is written in our "low-level
intermediate representation" (LIR).

You can [`EXPLAIN ANALYZE`](/sql/explain-analyze) an index or materialized view to
attribute performance information to each LIR operator.

## How do I troubleshoot slow queries?

Materialize stores a (sampled) log of the SQL statements that are issued against
your Materialize region in the last **24 hours**, along with various metadata
about these statements. You can access this log via the **"Query history"** tab
in the [Materialize console](/developer-tools/console/). You can filter
and sort statements by type, duration, and other dimensions.

This data is also available via the
[mz_internal.mz_recent_activity_log](/sql/system-catalog/mz_internal/#mz_recent_activity_log)
catalog table.

It's important to note that statements are sampled, so not all of them will be
captured in the log. In Materialize Cloud, the default and maximum sample rate
for most organizations is 99%, and Materialize may change it at any time. In
self-managed deployments, the maximum sample rate is set by the operator. See
[Query History](/self-managed-deployments/query-history/).

If you're looking for a complete audit history, use the [mz_audit_events](/sql/system-catalog/mz_catalog/#mz_audit_events)
catalog table, which records all DDL commands issued against your Materialize
region.

<!-- mz-docs page: serve-results/websocket-api -->

# Connect to Materialize via WebSocket
How to use Materialize via WebSocket

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

