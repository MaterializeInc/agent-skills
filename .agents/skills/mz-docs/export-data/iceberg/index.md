# Apache Iceberg
How to export results from Materialize to Apache Iceberg tables.
> **Public Preview:** This feature is in public preview.

Iceberg sinks provide exactly once delivery of updates from Materialize into
[Apache Iceberg](https://iceberg.apache.org/)[^1] tables. As data changes in
Materialize, the corresponding Iceberg tables are automatically kept up to date.
You can sink data from a materialized view, a source, or a table.

## Create an Iceberg sink

Materialize reaches your tables through an Iceberg catalog. Follow the guide for
the catalog hosting them:

- [AWS S3
  Tables](/export-data/iceberg-aws/)[^2], which authenticates through an
  AWS connection.
- [GCP BigLake](/export-data/iceberg-gcp/)[^3] <a class="private-preview-inline" href="https://materialize.com/preview-terms/">(feature in private preview)</a>
,
  which authenticates through a GCP connection.
- [Databricks Unity Catalog](/export-data/iceberg-databricks/)[^4] on
  AWS, which authenticates with the OAuth2 credentials of a Databricks service
  principal.

## Consume an Iceberg sink

A sink created with `MODE APPEND` writes a changelog rather than current state,
so consuming it means reconstructing current state from the `_mz_diff` column:

In append mode, the Iceberg table is a changelog rather than a snapshot of
current state, with two metadata columns added by the sink: `_mz_diff` and
`_mz_timestamp`. Every change is written as a data row: `_mz_diff` is `+1` for
an insertion and `-1` for a deletion, and an update appears as both rows,
sharing one `_mz_timestamp`.

A query engine reading the table can reconstruct current state in one of two
ways:

| Approach | How it works | When to use it |
| --- | --- | --- |
| Consolidate by diff | Group by every column of the Iceberg table except `_mz_diff` and `_mz_timestamp`, and keep the groups whose `_mz_diff` values sum to a positive number. | The sinked relation has no unique key, or you want a query that does not depend on one. |
| Latest version per key | Rank the rows within each key by `_mz_timestamp` descending, breaking ties on `_mz_diff` descending, then keep the top-ranked row where `_mz_diff` is `+1`. | The sinked relation has a unique key. Avoids grouping by every column, so it does not grow harder to write as the relation gets wider. |

Both approaches return the same result. Two details matter for correctness:

- An update writes `-1` and `+1` at the *same* `_mz_timestamp`, so ranking by
  timestamp alone is ambiguous. Breaking ties on `_mz_diff` descending is what
  selects the new version of the row rather than the old one.

- The latest row for a deleted key carries `_mz_diff = -1`, so filtering for
  `+1` after ranking is what removes deleted keys from the result.

Identifier quoting rules differ between query engines. Materialize creates
Iceberg identifiers in lowercase unless they were quoted when created, so
engines that resolve unquoted identifiers as uppercase require those
identifiers to be quoted.

For the query to do this in a specific engine's dialect, along with the setup
that engine requires, see:

- [Snowflake on AWS S3 Tables](/export-data/iceberg-aws-snowflake/)

[^1]:
    [Apache Iceberg](https://iceberg.apache.org/) is an open table format for
    large-scale analytics datasets.

[^2]:
    [Amazon S3
    Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html) is
    an AWS feature that provides fully managed Apache Iceberg tables as a native
    S3 storage type.

[^3]:
    [Google Cloud
    BigLake](https://cloud.google.com/biglake) provides a managed Apache Iceberg
    REST catalog over Google Cloud Storage.

[^4]:
    [Databricks Unity
    Catalog](https://docs.databricks.com/aws/en/external-access/iceberg) exposes
    its tables to Apache Iceberg clients through an Iceberg REST catalog
    endpoint.
