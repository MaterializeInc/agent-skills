# COMMIT
`COMMIT` ends a transaction block and commits all changes if the transaction statements succeed.
`COMMIT` ends the current [transaction](/sql/begin/#details). Upon the `COMMIT`
statement:

- If all transaction statements succeed, all changes are committed.

- If an error occurs, all changes are discarded; i.e., rolled back.

## Syntax

```mzsql
COMMIT;
```

## Details

[`BEGIN`](/sql/begin/) starts a transaction block. Once a transaction is started:
- Statements within the transaction are executed sequentially.
- A transaction ends with either a [`COMMIT`](/sql/commit/) or a
  [`ROLLBACK`](/sql/rollback/) statement.
  - If all transaction statements succeed and a [`COMMIT`](/sql/commit/) is
  [issued](/sql/commit/#details), all changes are saved.
  - If all transaction statements succeed and a [`ROLLBACK`](/sql/rollback/)
  is issued, all changes are discarded.
  - If an error occurs and either a [`COMMIT`](/sql/commit/) or a
  [`ROLLBACK`](/sql/rollback/) is issued, all changes are discarded.

Transactions in Materialize are **read-only** transactions, **write-only**
(more specifically, **insert-only**) transactions, or **DDL-only**
transactions.

For a [write-only (i.e., insert-only)
transaction](/sql/begin/#write-only-transactions), all statements in the
transaction are committed at the same timestamp.

For a [DDL-only transaction](/sql/begin/#ddl-only-transactions), all
statements in the transaction are committed at the same timestamp.

## Examples

### Commit a write-only transaction {#write-only-transactions}

In Materialize, write-only transactions are **insert-only** transactions.

An **insert-only** transaction block only contains [`INSERT`](/sql/insert/)
statements that insert into the **same** table.

On a successful [`COMMIT`](/sql/commit/), all statements from the
transaction are committed at the same timestamp.

```mzsql
BEGIN;
INSERT INTO orders VALUES (11,current_timestamp,'brownie',10);

-- Subsequent INSERTs must write to sales_items table only
-- Otherwise, the COMMIT will error and roll back the transaction.

INSERT INTO orders VALUES (11,current_timestamp,'chocolate cake',1);
INSERT INTO orders VALUES (11,current_timestamp,'chocolate chip cookie',20);
COMMIT;
```

If, within the transaction, a statement inserts into a table different from
that of the first statement, on [`COMMIT`](/sql/commit/), the transaction
encounters an **internal ERROR** and rolls back:

```none
ERROR:  internal error, wrong set of locks acquired
```

### Commit a read-only transaction

In Materialize, read-only transactions can be either:

- a `SELECT` only transaction that only contains [`SELECT`] statements or

- a `SUBSCRIBE`-based transactions that only contains a single[`DECLARE ...
  CURSOR FOR`] [`SUBSCRIBE`] statement followed by subsequent
  [`FETCH`](/sql/fetch) statement(s).

For example:

```mzsql
BEGIN;
DECLARE c CURSOR FOR SUBSCRIBE (SELECT * FROM flippers);

-- Subsequent queries must only FETCH from the cursor

FETCH 10 c WITH (timeout='1s');
FETCH 20 c WITH (timeout='1s');
COMMIT;
```

During the first query, a timestamp is chosen that is valid for all of the
objects referenced in the query. This timestamp will be used for all other
queries in the transaction.

> **Note:** The transaction will additionally hold back normal compaction of the objects,
> potentially increasing memory usage for very long running transactions.

## See also

- [`BEGIN`]
- [`ROLLBACK`]

[`BEGIN`]: /sql/begin/
[`ROLLBACK`]: /sql/rollback/
[`COMMIT`]: /sql/commit/
[`SELECT`]: /sql/select/
[`SUBSCRIBE`]: /sql/subscribe/
[`DECLARE ... CURSOR FOR`]: /sql/declare/
[`INSERT`]: /sql/insert
