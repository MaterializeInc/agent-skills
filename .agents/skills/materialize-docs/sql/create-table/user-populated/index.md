# CREATE TABLE: Read-write table
Create a read-write, user-populated table in Materialize.
Read-write tables let you read ([`SELECT`](/sql/select/)) and write
([`INSERT`](/sql/insert/), [`UPDATE`](/sql/update/), [`DELETE`](/sql/delete/))
to the table.

## Syntax

To create a new read-write table (i.e., users can perform
[`SELECT`](/sql/select/), [`INSERT`](/sql/insert/),
[`UPDATE`](/sql/update/), and [`DELETE`](/sql/delete/) operations):

```mzsql
CREATE [TEMP|TEMPORARY] TABLE [IF NOT EXISTS] <table_name> (
  <column_name> <column_type> [NOT NULL][DEFAULT <default_expr>]
  [, ...]
)
[WITH (
  PARTITION BY (<column_name> [, ...]) |
  RETAIN HISTORY [=] FOR <duration>
)]
;

```

| Syntax element | Description |
| --- | --- |
| **TEMP** / **TEMPORARY** | *Optional.* If specified, mark the table as temporary.  Temporary tables are: - Automatically dropped at the end of the session; - Not visible to other connections; - Created in the special `mz_temp` schema.  Temporary tables may depend upon other temporary database objects, but non-temporary tables may not depend on temporary objects.  |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<column_name>` |  The name of a column to be created in the new table. Names for columns must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<column_type>` |  The type of the column. For supported types, see [SQL data types](/sql/types/).  |
| **NOT NULL** | *Optional.* If specified, disallow  _NULL_ values for the column. Columns without this constraint can contain _NULL_ values.  |
| **DEFAULT <default_expr>** | *Optional.* If specified, use the `<default_expr>` as the default value for the column. If not specified, `NULL` is used as the default value.  |
| **WITH (<with_option>[,...])** |  The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `PARTITION BY (<column> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \| \| `RETAIN HISTORY <duration>` \| *Optional.* ***Private preview.** This option has known performance or stability issues and is under active development.* <br>If specified, Materialize retains historical data for the specified duration, which is useful to implement [durable subscriptions](/transform-data/patterns/durable-subscriptions/#history-retention-period).<br>Accepts positive [interval](/sql/types/interval/) values (e.g., `'1hr'`).\|  |

## Table names and column names

Names for tables and column(s) must follow the [naming
guidelines](/sql/identifiers/#naming-restrictions).

## Known limitations

Tables do not currently support:

- Primary keys
- Unique constraints
- Check constraints

See also the known limitations for [`INSERT`](/sql/insert#known-limitations),
[`UPDATE`](/sql/update#known-limitations), and [`DELETE`](/sql/delete#known-limitations).

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.
- For `CREATE TABLE ... FROM SOURCE`, `SELECT` privileges on the source and
  `USAGE` privileges on its schema. `SELECT` on a source permits attaching any
  reference that source ingests, so grant it only to roles that should be able
  to read all of the source's data.

## Examples

### Create a table

The following example uses `CREATE TABLE` to create a new read-write table
`mytable` with two columns `a` (of type `int`) and `b` (of type `text` and
not nullable):
```mzsql
CREATE TABLE mytable (a int, b text NOT NULL);

```

Once a user-populated table is created, you can perform CRUD
(Create/Read/Update/Delete) operations on it.

The following example uses [`INSERT`](/sql/insert/) to write two rows to the table:
```mzsql
INSERT INTO mytable VALUES
(1, 'hello'),
(2, 'goodbye')
;

```

The following example uses [`SELECT`](/sql/select/) to read all rows from the table:
```mzsql
SELECT * FROM mytable;

```The results should display the two rows inserted:

```hc {hl_lines="3-4"}
| a | b       |
| - | ------- |
| 1 | hello   |
| 2 | goodbye |
```

## Related pages

- [`INSERT`](/sql/insert/)
- [`DROP TABLE`](/sql/drop-table)
