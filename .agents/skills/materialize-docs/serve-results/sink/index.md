# Sink results

Sinking results from Materialize to external systems.

A [sink](/concepts/sinks/) describes the external system you want Materialize to
write data to and details the encoding of that data. You can sink data from a
**materialized** view, a source, or a table.

## Sink methods

To create a sink, you can:

| Method | External system | Guide(s) or Example(s) |
| --- | --- | --- |
| Use <code>COPY TO</code> command | Amazon S3 or S3-compatible storage | <ul> <li><a href="/serve-results/sink/s3/" >Sink to Amazon S3</a></li> </ul>  |
| Use Census as an intermediate step | Census supported destinations | <ul> <li><a href="/serve-results/sink/census/" >Sink to Census</a></li> </ul>  |
| Use <code>COPY TO</code> S3 or S3-compatible storage as an intermediate step | Snowflake and other systems that can read from S3 | <ul> <li><a href="/serve-results/sink/snowflake/" >Sink to Snowflake</a></li> </ul>  |
| Use a native connector | Kafka/Redpanda | <ul> <li><a href="/serve-results/sink/kafka/" >Sink to Kafka/Redpanda</a></li> </ul>  |
| Use the Kafka sink + Kafka Connect | Elasticsearch | <ul> <li><a href="/serve-results/sink/elasticsearch/" >Sink to Elasticsearch</a></li> </ul>  |
| Use the Kafka sink + Kafka Connect | OpenSearch | <ul> <li><a href="/serve-results/sink/opensearch/" >Sink to OpenSearch</a></li> </ul>  |
| Use the Kafka sink + <code>mz-tpuf-sink</code> | turbopuffer | <ul> <li><a href="/serve-results/sink/turbopuffer/" >Sink to turbopuffer</a></li> </ul>  |
| Use a native connector | Apache Iceberg hosted on AWS S3 Tables | <ul> <li><a href="/serve-results/sink/iceberg/" >Sink to Iceberg</a></li> </ul>  |
| Use <code>SUBSCRIBE</code> | Various | <ul> <li><a href="https://github.com/MaterializeInc/mz-catalog-sync" >Sink to Postgres</a></li> <li><a href="https://github.com/MaterializeIncLabs/mz-redis-sync" >Sink to Redis</a></li> </ul>  |

### Operational guideline

- Avoid putting sinks on the same cluster that hosts sources to allow for
[blue/green deployment](/manage/dbt/blue-green-deployments).

### Troubleshooting

For help, see [Troubleshooting
sinks](/serve-results/sink/sink-troubleshooting/).

---

## Amazon S3

This guide walks you through the steps required to export results from
Materialize to Amazon S3. Copying results to S3 is
useful to perform tasks like periodic backups for auditing, or downstream
processing in analytical data warehouses like [Snowflake](/serve-results/snowflake/),
Databricks or BigQuery.

## Before you begin

- Ensure you have access to an AWS account, and permissions to create and manage
  IAM policies and roles. If you're not an account administrator, you will need
  support from one!

## Step 1. Set up an Amazon S3 bucket

First, you must set up an S3 bucket and give Materialize enough permissions to
write files to it. We **strongly** recommend using [role assumption-based authentication](/sql/create-connection/#aws-permissions)
to manage access to the target bucket.

### Create a bucket

1. Log in to your AWS account.

1. Navigate to **AWS Services**, then **S3**.

1. Create a new, general purpose S3 bucket with the suggested default
   configurations.

### Create an IAM policy

Once you create an S3 bucket, you must associate it with an [IAM policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
that specifies what actions can be performed on the bucket by the Materialize
exporter role. For Materialize to be able to write data into the bucket, the
IAM policy must allow the following actions:

Action type  | Action name                                                                            | Action description
-------------|----------------------------------------------------------------------------------------|---------------
Write        | [`s3:PutObject`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html)      | Grants permission to add an object to a bucket.
List         | [`s3:ListBucket`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html) | Grants permission to list some or all of the objects in a bucket.
Write        | [`s3:DeleteObject`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html)| Grants permission to remove an object from a bucket.

To create a new IAM policy:

1. Navigate to **AWS Services**, then **AWS IAM**.

1. In the **IAM Dashboard**, click **Policies**, then **Create policy**.

1. For **Policy editor**, choose **JSON**.

1. Copy and paste the policy below into the editor, replacing `<bucket>` with
   the bucket name and `<prefix>` with the folder path prefix.

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                 "s3:PutObject",
                 "s3:DeleteObject"
               ],
               "Resource": "arn:aws:s3:::<bucket>/<prefix>/*"
           },
           {
               "Effect": "Allow",
               "Action": [
                   "s3:ListBucket"
               ],
               "Resource": "arn:aws:s3:::<bucket>",
               "Condition": {
                   "StringLike": {
                       "s3:prefix": [
                           "<prefix>/*"
                       ]
                   }
               }
           }
       ]
   }
   ```

1. Click **Next**.

1. Enter a name for the policy, and click **Create policy**.

### Create an IAM role

Next, you must attach the policy you just created to a Materialize-specific
[IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html).

1. Navigate to **AWS Services**, then **AWS IAM**.

1. In the **IAM Dashboard**, click **Roles**, then **Create role**.

1. In **Trusted entity type**, select **Custom trust policy**, and copy and
   paste the policy below.

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Principal": {
                   "AWS": "arn:aws:iam::664411391173:role/MaterializeConnection"
               },
               "Action": "sts:AssumeRole",
               "Condition": {
                   "StringEquals": {
                       "sts:ExternalId": "PENDING"
                   }
               }
           }
       ]
   }
   ```

   Materialize **always uses the provided IAM principal** to assume the role, and
   also generates an **external ID** which uniquely identifies your AWS connection
   across all Materialize regions (see [AWS connection permissions](/sql/create-connection/#aws-permissions)).
   For now, you'll set this ID to a dummy value; later, you'll update it with
   the unique identifier for your Materialize region.

1. Click **Next**.

1. In **Add permissions**, select the IAM policy you created in [Create an IAM policy](#create-an-iam-policy),
   and click **Next**.

1. Enter a name for the role, and click **Create role**.

1. Click **View role** to see the role summary page, and note down the
   role **ARN**. You will need it in the next step to create an AWS connection in
   Materialize.

## Step 2. Create a connection

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, create an [AWS connection](/sql/create-connection/#aws),
   replacing `<account-id>` with the 12-digit number that identifies your
   AWS account, and  `<role>` with the name of the role you created in the
   previous step:

   ```mzsql
   CREATE CONNECTION aws_connection
      TO AWS (ASSUME ROLE ARN = 'arn:aws:iam::<account-id>:role/<role>');
   ```

1. Retrieve the external ID for the connection:

   ```mzsql
   SELECT awsc.id, external_id
    FROM mz_internal.mz_aws_connections awsc
    JOIN mz_connections c ON awsc.id = c.id
    WHERE c.name = 'aws_connection';
   ```

   The external ID will have the following format:

   ```text
   mz_XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX_uXXX
   ```

1. In your AWS account, find the IAM role you created in [Create an IAM role](#create-an-iam-role)
   and, under **Trust relationships**, click **Edit trust policy**. Use the
   `external_id` from the previous step to update the trust policy's
   `sts:ExternalId`, then click **Update policy**.

   > **Warning:** Failing to constrain the external ID in your role trust policy
>    will allow other Materialize customers to assume your role and use AWS
>    privileges you have granted the role!

1. Back in Materialize, validate the AWS connection you created using the
   [`VALIDATE CONNECTION`](/sql/validate-connection) command.

   ```mzsql
   VALIDATE CONNECTION aws_connection;
   ```

   If no validation error is returned, you're ready to use this connection to
   run a bulk export from Materialize to your target S3 bucket! 🔥

## Step 3. Run a bulk export

To export data to your target S3 bucket, use the [`COPY TO`](/sql/copy-to/#copy-to-s3)
command, and the AWS connection you created in the previous step.

**Parquet:**

```mzsql
COPY some_object TO 's3://<bucket>/<path>'
WITH (
    AWS CONNECTION = aws_connection,
    FORMAT = 'parquet'
  );
```

For details on the Parquet writer settings Materialize uses, as well as data
type support and conversion, check the [reference documentation](/sql/copy-to/#copy-to-s3-parquet).

**CSV:**

```mzsql
COPY some_object TO 's3://<bucket>/<path>'
WITH (
    AWS CONNECTION = aws_connection,
    FORMAT = 'csv'
  );
```

You might notice that Materialize first writes a sentinel file to the target S3
bucket. When the copy operation is complete, this file is deleted. This allows
using the [`s3:ObjectRemoved` event](https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-event-types-and-destinations.html#supported-notification-event-types)
to trigger downstream processing.

## Step 4. (Optional) Add scheduling

Bulk exports to Amazon S3 using the `COPY TO` command are _one-shot_: every time
you want to export results, you must run the command. To automate running bulk
exports on a regular basis, you can set up scheduling, for example using a
simple `cron`-like service or an orchestration platform like Airflow or
Dagster.

---

## Apache Iceberg

> **Public Preview:** This feature is in public preview.

Iceberg sinks provide exactly once delivery of updates from Materialize into
[Apache Iceberg](https://iceberg.apache.org/)[^1] tables hosted on either
[Amazon S3
Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html)[^2]
or [Google Cloud BigLake](https://cloud.google.com/biglake)[^3]. As data
changes in Materialize, the corresponding Iceberg tables are automatically
kept up to date. You can sink data from a materialized view, a source, or a
table.

Follow the guide for the platform hosting your Iceberg tables:

- [AWS S3 Tables](/serve-results/sink/iceberg-aws/)
- [GCP BigLake](/serve-results/sink/iceberg-gcp/) <a class="private-preview-inline" href="https://materialize.com/preview-terms/">(feature in private preview)</a>

[^1]: [Apache Iceberg](https://iceberg.apache.org/) is an open table format for
large-scale analytics datasets.

[^2]: [Amazon S3
Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html) is
    an AWS feature that provides fully managed Apache Iceberg tables as a native
    S3 storage type.

[^3]: [Google Cloud
BigLake](https://cloud.google.com/biglake) provides a managed Apache Iceberg
    REST catalog over Google Cloud Storage.

---

## AWS S3 Tables

> **Public Preview:** This feature is in public preview.

This guide walks you through the steps required to set up Iceberg sinks in
Materialize Cloud.

## Prerequisites

- An AWS account with permissions to create and manage IAM policies and roles.
- An AWS S3 Table bucket in your AWS account. The S3 Table bucket must be in
  the same AWS region as your Materialize deployment.
- A namespace in the AWS S3 Table bucket. For details on creating namespaces,
  see [AWS S3 documentation: Creating a namespace](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-namespace-create.html).

## Create the Iceberg catalog connection in Materialize

### Step 1. Set up permissions in AWS

In AWS, set up permissions to allow Materialize to write data files to the
object storage backing your Iceberg catalog. This tutorial uses an IAM policy
and IAM role to grant the required permissions. We **strongly** recommend using
[role assumption-based authentication](/sql/create-connection/#aws-permissions)
to manage access.

#### Step 1A. Create an IAM policy

Create an [IAM
policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
that allows full access to your S3 Tables API.Replace `<S3 table bucket ARN>`
with the ARN of your S3 table bucket:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3tables:*",
            "Resource": [
                "<S3 table bucket ARN>",
                "<S3 table bucket ARN>/table/*"
            ]
        }
    ]
}
```

#### Step 1B. Create an IAM role

Create an [IAM
role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) that
Materialize can assume.

1. For the **Trusted entity type**, specify **Custom trust policy** with the
following:
    - `Principal`: The example uses the [Materialize Cloud IAM
      principal](/sql/create-connection/#aws-permissions). For self-managed
      deployments and the Emulator, the principal will differ.
    - `ExternalId`: `"PENDING"` is a placeholder and will be updated after
    creating the AWS connection in Materialize.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::664411391173:role/MaterializeConnection"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": "PENDING"
                    }
                }
            }
        ]
    }
    ```

1. For permissions, add the [IAM policy created
   earlier](#step-1a-create-an-iam-policy) to grant access to the S3 Tables.

Once you have created the IAM role, copy the role ARN from the AWS console.
You'll use the ARN in the next step.

### Step 2. Create an AWS connection in Materialize

In Materialize, create an **AWS connection** to authenticate with the object
storage:

1. Use [`CREATE CONNECTION ... TO AWS`](/sql/create-connection/#aws) to create
   an AWS connection, replacing:

   - `<IAM role ARN>` with your IAM role ARN from [step
     1](#step-1b-create-an-iam-role)
   - `<region>` with your AWS region (e.g., `us-east-1`):

    ```mzsql
    CREATE CONNECTION aws_connection TO AWS (
        ASSUME ROLE ARN = '<IAM role ARN>',
        REGION = '<region>'
    );
    ```

    For more details on AWS connection options, see [`CREATE
    CONNECTION`](/sql/create-connection/#aws).

1. Fetch the `external_id` for your connection, replacing `<IAM role ARN>` with
    your IAM role ARN:

   ```mzsql
   SELECT external_id
   FROM mz_internal.mz_aws_connections awsc
   JOIN mz_connections c ON awsc.id = c.id
   WHERE c.name = 'aws_connection'
   AND awsc.assume_role_arn = '<iam-role-arn>';
   ```

   You will use the `external_id` to update the IAM role in the next step.

### Step 3. Update the IAM role in AWS

Once you have the `external_id`, update the trust policy for the IAM role
created in [step 1](#step-1b-create-an-iam-role). Replace `"PENDING"` with your
external ID value. Your IAM trust policy should look like the following (but
with your external ID value):

```json{hl_lines="12"}
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::664411391173:role/MaterializeConnection"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "mz_1234abcd-5678-efgh-9012-ijklmnopqrst_u123"
                }
            }
        }
    ]
}
```

### Step 4. Create an Iceberg catalog connection in Materialize

In Materialize, create an **Iceberg catalog connection** for the Iceberg sink to
use. To create, use [`CREATE CONNECTION ... TO ICEBERG
CATALOG`](/sql/create-connection/#iceberg-catalog), replacing:
- `<region>` with your AWS region (e.g., `us-east-1`) and
- `<S3 table bucket ARN>` with your AWS S3 Table bucket ARN.

The command uses the AWS connection you created earlier.

```mzsql
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 's3tablesrest',
    URL = 'https://s3tables.<region>.amazonaws.com/iceberg',
    WAREHOUSE = '<S3 table bucket ARN>',
    AWS CONNECTION = aws_connection
);
```

## Create the Iceberg sink in Materialize

> **Note:** `CREATE SINK` no longer includes a `USING AWS CONNECTION` clause.
> Instead, the sink inherits credentials from the [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog).
> Existing Iceberg sinks are not affected and will continue to function as before.

In Materialize, you can sink from a materialized view, table, or source. Use
[`CREATE SINK`](/sql/create-sink/iceberg) to create an Iceberg sink, replacing:

- `<sink_name>` with a name for your sink.
- `<sink_cluster>` with the name of your sink cluster.
- `<my_materialize_object>` with the name of your materialized view, table, or source.
- `<my_iceberg_namespace>` with your catalog namespace.
- `<my_iceberg_table>` with the name of your Iceberg table. If the Iceberg table
  does not exist, Materialize creates the table. For details, see [`CREATE SINK`
  reference page](/sql/create-sink/iceberg/#iceberg-table-creation).
- `<commit_interval>` with your commit interval (e.g., `1m`). The commit
  interval specifies how frequently Materialize commits snapshots to Iceberg.
  The minimum commit interval is `1s`. See [Commit interval
  tradeoffs](#commit-interval-tradeoffs) below.

For the full list of syntax options, see the [`CREATE SINK` reference](/sql/create-sink/iceberg).

### Upsert mode

In upsert mode, replace `<key>` with the column(s) that uniquely identify rows.
```mzsql
CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<my_iceberg_namespace>',
    TABLE = '<my_iceberg_table>'
  )
  KEY (<key>)
  MODE UPSERT
  WITH (COMMIT INTERVAL = '<commit_interval>');

```

### Append mode

In append mode, no `KEY` clause is used. The Iceberg table includes all source
columns plus `_mz_diff` (`int`) and `_mz_timestamp` (`long`).
```mzsql
CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<my_iceberg_namespace>',
    TABLE = '<my_iceberg_table>'
  )
  MODE APPEND
  WITH (COMMIT INTERVAL = '<commit_interval>');

```

## Considerations

### Commit interval tradeoffs {#commit-interval-tradeoffs}

The `COMMIT INTERVAL` setting controls how frequently Materialize commits
snapshots to your Iceberg table, making the data available to downstream query
engines. This setting involves tradeoffs:

| Shorter intervals (e.g., < `1m`) | Longer intervals (e.g., `5m`) |
|---------------------------------|-------------------------------|
| Lower latency - data visible sooner in downstream systems | Higher latency - data takes longer to appear |
| More small files - can degrade query performance over time | Fewer, larger files - better query performance |
| More frequent snapshot commits - higher catalog overhead | Less catalog overhead |
| Lower throughput efficiency | Higher throughput efficiency |

**Recommendations:**
- For production, use intervals of `1m` or longer
- For batch analytics, use longer intervals (`5m` to `15m`)

Starting in v26.34, you can change the commit interval of an existing sink with
[`ALTER SINK`](/sql/alter-sink/).

> **Note:** Outside of development environments, commit intervals should be at least `1m`.
> Short commit intervals increase catalog overhead and produce many small files.
> Small files will result in degraded query performance. It also increases load on
> the Iceberg metadata, which can result in a degraded catalog, and non-responsive
> queries.

### Exactly-once delivery

Iceberg sinks provide **exactly-once delivery**. After a restart,
Materialize resumes from the last committed snapshot without duplicating
data.

Materialize stores progress information in Iceberg snapshot metadata
properties (`mz-frontier` and `mz-sink-version`).

### Type mapping

Materialize converts SQL types to Iceberg/Parquet types:

| SQL type | Iceberg type |
|----------|--------------|
| `boolean` | `boolean` |
| `smallint`, `integer` | `int` |
| `uint2` | `int` |
| `bigint` | `long` |
| `uint4` | `long` |
| `uint8` | `decimal(20, 0)` |
| `real` | `float` |
| `double precision` | `double` |
| `numeric` | `decimal(38, scale)` |
| `date` | `date` |
| `time` | `time` (microsecond) |
| `timestamp` | `timestamp` (microsecond) |
| `timestamptz` | `timestamptz` (microsecond) |
| `text`, `varchar` | `string` |
| `bytea` | `binary` |
| `uuid` | `fixed(16)` |
| `jsonb` | `string` |
| `interval` | `string` |
| `int4range`, `int8range`, `numrange`, `daterange`, `tsrange`, `tstzrange` | `struct` (fields: `lower`, `upper`, `lower_inclusive`, `upper_inclusive`, `empty`) |
| `record` | `struct` |
| `list` | `list` |
| `map` | `map` |

### Limitations

- Your S3 Tables bucket must be in the same AWS region as your Materialize
deployment.

- Partitioned tables are not supported.

- Schema evolution of an Iceberg table is not supported. If the `SINK FROM` object's schema changes, you must drop and recreate the sink.

## Troubleshooting

### Sink creation fails with "input compacted past resume upper"

This error occurs when the source data has been compacted beyond the point where
the sink last committed. This can happen after a Materialize backup/restore
operation. You may need to drop and recreate the sink, which will re-snapshot
the entire source relation.

### Commit conflicts

If another process modifies the Iceberg table while Materialize is committing,
you may see commit conflict errors. Materialize will automatically retry, but
if conflicts persist, ensure no other writers are modifying the same table.

## Related pages

- [`CREATE SINK`](/sql/create-sink/iceberg)
- [`CREATE CONNECTION`](/sql/create-connection)
- [Apache Iceberg documentation](https://iceberg.apache.org/docs/latest/)

---

## Census

This guide walks you through the steps required to create a [Census](https://www.getcensus.com/) sync using Materialize.

## Before you begin

In order to build a sync with Census you will need:

* A table, view, materialized view or source within your Materialize account that you would like to export.
* A [Braze](https://www.braze.com/) account. Census supports a number of possible [destinations](https://www.getcensus.com/integrations), we will use Braze as an example.

## Step 1. Set up a Materialize Source

To begin you will need to add your Materialize database as a source in Census.

1. In Census, navigate to **Sources** and then click **New Source**.

1. From the list of connection types, choose **Materialize**.

1. Set the connection parameters using the credentials provided in the [Materialize console](/console/).
   Then click the **Connect** button.

## Step 2. Set up a Destination

Next you will add a destination where data will be sent.

**Braze:**

1. In Census, navigate to **Destinations** and then click **New Destination**.

1. From the list of destinations types, choose **Braze**.

1. You will need to supply your Braze URL (which will most likely be `https://rest.iad-03.braze.com`) and a Braze API key.
   The [Census guide for Braze](https://docs.getcensus.com/destinations/braze) will explain how to create an API key with the
   correct permissions. Then click the **Connect**.

## Step 3. Create a Sync

After successfully adding the Materialize source, you can create a sync to send data from Materialize to your downstream destination.

**Braze:**

1. In Census, navigate to **Syncs** and then click **New Sync**.

1. Under **Select a Source** choose **Select a Warehouse Table**. Using the drop-down, choose the Materialize source that was
   configured in step 1 as the **Connection**. Using the **Schema** and **Table** drop-downs you can select the
   Materialize object you would like to export.

1. Under **Select a Destination** choose the Braze destination configured in step 2 and select "User" as the **Object**.

1. Under **Select Sync Behavior** can be set to "Update or Create". This will only add and modify new data in Braze but never delete users.

1. Under **Select a Sync Key** select an id column from the Materialize object.

1. Under **Set Up Braze Field Mappings** set any of the columns in the Materialize object to their corresponding fields in the Braze User entity.

1. Click **Next** to see an overview of your sync and click **Create** to create the sync.

## Step 4. Add a Schedule (Optional)

Your Census sync is created and ready to run. It can be invoked manually but a schedule will ensure all new data
is sent to the destination.

1. In Census navigate to **Syncs** and select the sync that was just created.

1. Within your sync toolbar click **Configuration**. In **Sync Trigger > Schedule** you can select from a number of
   difference schedules. If you are using a source or materialized view as your source object, you can choose "Continuous"
   and Census will retrieve new data as soon as it exists within Materialize.

---

## Elasticsearch

This guide shows how to send results from Materialize to Elasticsearch. A
[Kafka sink](/sql/create-sink/kafka/) writes the results to a Kafka topic.
Kafka Connect reads that topic and writes the documents to Elasticsearch.

Use this pipeline to keep an Elasticsearch search index up to date to within
hundreds of milliseconds, just using SQL. Materialize maintains the search
document as an incrementally updated view over your operational data, and
pushes precise deltas to Elasticsearch as upstream data changes, so only the
affected documents are rewritten.

In this guide, we also use
[`perfect-embedding`](https://github.com/MaterializeInc/perfect-embedding), a
Kafka Connect SMT (single message transform) that we developed.
`perfect-embedding` runs inside the connector and compares the `before` and
`after` values of each change to find the columns that actually changed. It
recomputes a vector embedding only for those columns, so embedding costs scale
with what changed rather than with how often the pipeline runs.

## Before you begin

- An Elasticsearch 7.x or 8.x cluster. The self-managed connector does not
  work with Elasticsearch 9.x. For Elasticsearch 9.x, use the Confluent
  Cloud managed [Elasticsearch Sink
  V2](https://docs.confluent.io/cloud/current/connectors/cc-elasticsearch-sink-v2/cc-elasticsearch-sink-v2.html)
  connector instead.

- Kafka Connect workers that run in distributed mode. Each worker needs a
  writable `plugin.path` and Java 11 or later.

- An Elasticsearch role for the connector. Grant this role `read`, `write`,
  `view_index_metadata`, and `create_index` on the target index.

- A Kafka or Redpanda cluster. Materialize and the destination system must
  both connect to this cluster.

- A materialized view, source, or table to export. A sink cannot read
  from a plain view.

- A cluster to run the sink. Name this cluster with `IN CLUSTER`. See
  [`CREATE CLUSTER`](/sql/create-cluster/). When a sink starts, it loads a
  full snapshot of the relation into memory. Size the cluster for the
  snapshot, not for the steady-state rate of change.

- The [Kafka ACLs](/sql/create-sink/kafka/#required-kafka-acls) that the sink
  needs.

You also need these privileges in Materialize:

- `CREATE` privileges on the containing schema.
- `SELECT` privileges on the item being written out to an external system.
  - NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to
    execute the view definition.
- `CREATE` privileges on the containing cluster if the sink is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the sink is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the sink definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Step 1. Set up the sink in Materialize

The examples in this guide build a search document for an article catalog tracking its content and page views.

### Create the connections

```mzsql
CREATE SECRET kafka_password AS '<BROKER_PASSWORD>';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER '<BROKER_HOST>:9092',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = '<BROKER_USERNAME>',
    SASL PASSWORD = SECRET kafka_password
);

CREATE SECRET csr_password AS '<CSR_PASSWORD>';

CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
    URL '<CSR_URL>',
    USERNAME = '<CSR_USERNAME>',
    PASSWORD = SECRET csr_password
);
```

The embedding transform compares structured records to find changes, so this
pipeline needs Avro with a schema registry. For other authentication
methods, see [`CREATE CONNECTION`](/sql/create-connection/#kafka).

### Create the search document

Create a [materialized view](/sql/create-materialized-view/) that builds the
document you want to search.

```mzsql
CREATE MATERIALIZED VIEW articles AS
    SELECT a.id, a.title, a.body, count(p.article_id) AS views
    FROM article_content a
    LEFT JOIN page_views p ON a.id = p.article_id
    GROUP BY 1, 2, 3;
```

### Create the sink

```mzsql
CREATE SINK articles_sink_v1
  IN CLUSTER sinks_cluster
  FROM articles
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'articles_v1',
    TOPIC PARTITION COUNT 6
  )
  KEY (id) NOT ENFORCED
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE DEBEZIUM;
```

`ENVELOPE DEBEZIUM` wraps each change in a `{"before": ..., "after": ...}`
value. The transform compares these two fields to find the columns that
changed. The transform also converts each delete into a tombstone. The
connector applies this tombstone as a document delete. For the full list of
options, see [`CREATE SINK ... INTO KAFKA`](/sql/create-sink/kafka/).

## Step 2. Create the Elasticsearch index

The connector writes documents to an index. The index name is the Kafka
topic name in lowercase letters. The sink topic is `articles_v1`, so the
index name is also `articles_v1`.

Create an empty index named `articles_v1`. The sink fills this index later.

Declare the index mapping yourself. The connector **does not infer** a
`dense_vector` field. An index that the connector creates cannot serve
vector queries.

```nofmt
PUT /articles_v1
{
  "mappings": {
    "properties": {
      "id":    { "type": "integer" },
      "title": { "type": "text" },
      "body":  { "type": "text" },
      "views": { "type": "long" },
      "title_embedding": {
        "type": "dense_vector",
        "dims": 1536,
        "similarity": "cosine"
      },
      "body_embedding": {
        "type": "dense_vector",
        "dims": 1536,
        "similarity": "cosine"
      }
    }
  }
}
```

The output should resemble the following:

```nofmt
{ "acknowledged": true, "shards_acknowledged": true, "index": "articles_v1" }
```

For the list of vector options, see Elastic's [`dense_vector` field
reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html).

Create a read alias named `articles`. Applications send queries to this
alias, not to the index `articles_v1` directly:

```nofmt
POST /_aliases
{
  "actions": [
    { "add": { "index": "articles_v1", "alias": "articles" } }
  ]
}
```

The output should resemble the following:

```nofmt
{ "acknowledged": true }
```

> **Warning:** A new sink's snapshot inserts only the rows that exist when it starts. The
> snapshot does not remove old documents from the destination.
> Do not point a new sink at a destination that already holds documents. Those
> documents stay in the destination. No later write removes them.

## Step 3. Deploy the connector

1. Install the [Confluent Elasticsearch Sink
   Connector](https://docs.confluent.io/kafka-connectors/elasticsearch/current/overview.html)
   from Confluent Hub.
1. Extract the
   [`perfect-embedding`](https://github.com/MaterializeInc/perfect-embedding/releases)
   release zip file into a directory on the worker's `plugin.path`.
1. Restart the workers. Kafka Connect then finds both plugins.

Create the connector. Send this configuration to the Kafka Connect REST API
with `POST /connectors`:

```json
{
  "name": "elasticsearch-articles",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "topics": "articles_v1",
    "connection.url": "https://<ELASTICSEARCH_HOST>:9200",
    "connection.username": "<ELASTICSEARCH_USERNAME>",
    "connection.password": "<ELASTICSEARCH_PASSWORD>",
    "tasks.max": "4",
    "key.ignore": "false",
    "schema.ignore": "false",
    "write.method": "UPSERT",
    "behavior.on.null.values": "delete",
    "max.in.flight.requests": "1",
    "read.timeout.ms": "30000",
    "batch.size": "100",
    "consumer.override.isolation.level": "read_committed",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "<CSR_URL>",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "<CSR_URL>",
    "transforms": "extractKey,embed",
    "transforms.extractKey.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    "transforms.extractKey.field": "id",
    "transforms.embed.type": "com.materialize.connect.smt.embedding.EmbeddingDiffTransform",
    "transforms.embed.embedded.columns": "title,body",
    "transforms.embed.provider": "openai",
    "transforms.embed.openai.api.key": "${file:/opt/connect/secrets.properties:openai_api_key}",
    "transforms.embed.openai.model": "text-embedding-3-small",
    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "dlq.elasticsearch.articles_v1",
    "errors.deadletterqueue.context.headers.enable": "true"
  }
}
```

The `${file:...}` reference needs the file config provider. Enable this
provider in the worker properties. Set `config.providers=file` and
`config.providers.file.class=org.apache.kafka.common.config.provider.FileConfigProvider`.

The `embed` transform updates the vectors. For each record, it reads the
Debezium `before` and `after` values. It recomputes an embedding only for a
column in `embedded.columns` whose value changed. It leaves the rest of the
document unchanged:

- `transforms.embed.embedded.columns` names the text columns to embed. Each
  column must have the string type.
- `transforms.embed.provider` selects the embedding provider. This example
  uses `openai`.
- `transforms.embed.openai.api.key` and `transforms.embed.openai.model`
  configure the OpenAI client. The connector reads these settings only when
  `provider` is `openai`.

For the other transform options, see the
[`perfect-embedding`](https://github.com/MaterializeInc/perfect-embedding)
documentation.

## Step 4. Validate the pipeline

1.  Check that the connector is running:

    ```nofmt
    GET /connectors/elasticsearch-articles/status
    ```

    The output should resemble the following:

    ```nofmt
    {
      "name": "elasticsearch-articles",
      "connector": { "state": "RUNNING" },
      "tasks": [ { "id": 0, "state": "RUNNING" } ]
    }
    ```

1.  Confirm that the documents have their vectors. Use the `fields` parameter
    to request the vector field. This parameter returns the vector field even
    when the index excludes vectors from `_source`:

    ```nofmt
    GET /articles/_search
    {
      "size": 1,
      "_source": [ "id", "title", "views" ],
      "fields": [ "title_embedding" ]
    }
    ```

    The output should resemble the following:

    ```nofmt
    "hits": [
      {
        "_id": "1",
        "_source": { "id": 1, "title": "Storage engines", "views": 42 },
        "fields": { "title_embedding": [ [ 0.021, -0.118, ... ] ] }
      }
    ]
    ```

1.  Delete the row with `id = 1` from `article_content` in Materialize:

    ```mzsql
    DELETE FROM article_content WHERE id = 1;
    ```

    Confirm that the document is gone:

    ```nofmt
    GET /articles/_doc/1
    ```

    The response reports `"found": false`.

## Related pages

- [`CREATE SINK ... INTO KAFKA`](/sql/create-sink/kafka/)
- [`CREATE CONNECTION`](/sql/create-connection/#kafka)
- [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/)
- [Sinks](/concepts/sinks/)
- [Kafka and Redpanda](/serve-results/sink/kafka/)
- [Troubleshooting sinks](/serve-results/sink/sink-troubleshooting/)

---

## GCP BigLake

> **Warning:** [Iceberg tables managed by the Lakehouse runtime catalog (BigLake API)](https://docs.cloud.google.com/lakehouse/docs/key-concepts#metastore-iceberg)
> do not receive automated maintenance like expiring old snapshots and compacting manifests and data files.
> Without table maintenance, table metadata grows over time and will eventually exceed BigLake's allowed limit.
> This will prevent Materialize Iceberg sinks from committing new data.
> [Iceberg tables managed by BigQuery](https://docs.cloud.google.com/lakehouse/docs/key-concepts#iceberg-managed-tables)
> do receive automated maintenance, but only BigQuery can write to them.

This guide walks you through the steps required to set up Iceberg sinks in
Materialize Cloud.

## Prerequisites

- Google Cloud project with the [BigLake API enabled](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog#before_you_begin).
- Google Cloud [Storage bucket](https://console.cloud.google.com/storage/browser) to serve as the Iceberg warehouse.
- [Lakehouse runtime catalog](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog#create_a_catalog) backed by your warehouse bucket.
  For **Authentication method**, you can select either _End-user credentials_ or _Credential vending mode_.
  Materialize authenticates separately with a [GCP service account key](https://docs.cloud.google.com/iam/docs/keys-create-delete#iam-service-account-keys-create-gcloud)
  (provided in the next step), so both modes work.
- [Namespace in the catalog](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog#create_a_namespace_or_schema).

## Create the Iceberg catalog connection in Materialize

### Step 1. Set up permissions in GCP

Materialize uses a Google Cloud [service account](https://docs.cloud.google.com/iam/docs/service-account-overview) to
authenticate to BigLake.

1. Create the [service account](https://console.cloud.google.com/iam-admin/serviceaccounts).
2. Grant the service account these roles on your **project**:
    - `biglake.editor` (BigLake Editor)
    - `serviceusage.serviceUsageConsumer` (Service Usage Consumer)
3. Grant the service account this role on your **Iceberg warehouse bucket**:
    - `storage.objectUser` (Storage Object User)
4. [Create a service account key in JSON format.](https://docs.cloud.google.com/iam/docs/keys-create-delete#iam-service-account-keys-create-gcloud)

5. Base64-encode the entire JSON key (e.g. `base64 < sa_key.json`). In the [next
   step](#step-2-create-a-gcp-connection-and-iceberg-catalog-connection-in-materialize),
   you will decode the resulting string in the `CREATE SECRET` statement.
   Encoding the key first and decoding it in the `CREATE SECRET` statement
   avoids escaping quotes and newlines in the SQL string literal.

### Step 2. Create a GCP connection and Iceberg catalog connection in Materialize

The following example creates a [GCP connection](/sql/create-connection/#gcp) and an [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) for Google Cloud BigLake:
```mzsql
-- Using the base64-encoded service account key (e.g. base64 < sa_key.json)
CREATE SECRET gcp_service_account_key
  AS decode('<base64-encoded service account key JSON>', 'base64');

-- Create a GCP connection that uses the service-account key.
CREATE CONNECTION gcp_connection TO GCP (
    SERVICE ACCOUNT KEY = SECRET gcp_service_account_key
);

-- Create the Iceberg catalog connection pointing to BigLake.
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://biglake.googleapis.com/iceberg/v1/restcatalog',
    WAREHOUSE = 'gs://<bucket>',
    GCP CONNECTION = gcp_connection
);

```

## Create the Iceberg sink in Materialize

In Materialize, you can sink from a materialized view, table, or source. Use
[`CREATE SINK`](/sql/create-sink/iceberg) to create an Iceberg sink, replacing:

- `<sink_name>` with a name for your sink.
- `<sink_cluster>` with the name of your sink cluster.
- `<my_materialize_object>` with the name of your materialized view, table, or source.
- `<my_iceberg_namespace>` with your catalog namespace.
- `<my_iceberg_table>` with the name of your Iceberg table. If the Iceberg table
  does not exist, Materialize creates the table. For details, see [`CREATE SINK`
  reference page](/sql/create-sink/iceberg/#iceberg-table-creation).
- `<commit_interval>` with your commit interval (e.g., `1m`). The commit
  interval specifies how frequently Materialize commits snapshots to Iceberg.
  The minimum commit interval is `1s`. See [Commit interval
  tradeoffs](#commit-interval-tradeoffs) below.

For the full list of syntax options, see the [`CREATE SINK` reference](/sql/create-sink/iceberg).

### Upsert mode

In upsert mode, replace `<key>` with the column(s) that uniquely identify rows.
```mzsql
CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<my_iceberg_namespace>',
    TABLE = '<my_iceberg_table>'
  )
  KEY (<key>)
  MODE UPSERT
  WITH (COMMIT INTERVAL = '<commit_interval>');

```

### Append mode

In append mode, no `KEY` clause is used. The Iceberg table includes all source
columns plus `_mz_diff` (`int`) and `_mz_timestamp` (`long`).
```mzsql
CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<my_iceberg_namespace>',
    TABLE = '<my_iceberg_table>'
  )
  MODE APPEND
  WITH (COMMIT INTERVAL = '<commit_interval>');

```

## Considerations

### Commit interval tradeoffs {#commit-interval-tradeoffs}

The `COMMIT INTERVAL` setting controls how frequently Materialize commits
snapshots to your Iceberg table, making the data available to downstream query
engines. This setting involves tradeoffs:

| Shorter intervals (e.g., < `1m`) | Longer intervals (e.g., `5m`) |
|---------------------------------|-------------------------------|
| Lower latency - data visible sooner in downstream systems | Higher latency - data takes longer to appear |
| More small files - can degrade query performance over time | Fewer, larger files - better query performance |
| More frequent snapshot commits - higher catalog overhead | Less catalog overhead |
| Lower throughput efficiency | Higher throughput efficiency |

**Recommendations:**
- For production, use intervals of `1m` or longer
- For batch analytics, use longer intervals (`5m` to `15m`)

Starting in v26.34, you can change the commit interval of an existing sink with
[`ALTER SINK`](/sql/alter-sink/).

> **Note:** Outside of development environments, commit intervals should be at least `1m`.
> Short commit intervals increase catalog overhead and produce many small files.
> Small files will result in degraded query performance. It also increases load on
> the Iceberg metadata, which can result in a degraded catalog, and non-responsive
> queries.

### Exactly-once delivery

Iceberg sinks provide **exactly-once delivery**. After a restart,
Materialize resumes from the last committed snapshot without duplicating
data.

Materialize stores progress information in Iceberg snapshot metadata
properties (`mz-frontier` and `mz-sink-version`).

### Type mapping

Materialize converts SQL types to Iceberg/Parquet types:

| SQL type | Iceberg type |
|----------|--------------|
| `boolean` | `boolean` |
| `smallint`, `integer` | `int` |
| `uint2` | `int` |
| `bigint` | `long` |
| `uint4` | `long` |
| `uint8` | `decimal(20, 0)` |
| `real` | `float` |
| `double precision` | `double` |
| `numeric` | `decimal(38, scale)` |
| `date` | `date` |
| `time` | `time` (microsecond) |
| `timestamp` | `timestamp` (microsecond) |
| `timestamptz` | `timestamptz` (microsecond) |
| `text`, `varchar` | `string` |
| `bytea` | `binary` |
| `uuid` | `fixed(16)` |
| `jsonb` | `string` |
| `interval` | `string` |
| `int4range`, `int8range`, `numrange`, `daterange`, `tsrange`, `tstzrange` | `struct` (fields: `lower`, `upper`, `lower_inclusive`, `upper_inclusive`, `empty`) |
| `record` | `struct` |
| `list` | `list` |
| `map` | `map` |

### Limitations

- [Iceberg tables managed by the Lakehouse runtime catalog (BigLake API)](https://docs.cloud.google.com/lakehouse/docs/key-concepts#metastore-iceberg)
do not receive automated maintenance like expiring old snapshots and compacting manifests and data files.

Without table maintenance, table metadata grows over time and will eventually exceed BigLake's allowed limit.
This will prevent Materialize Iceberg sinks from committing new data.

- [Iceberg tables managed by BigQuery](https://docs.cloud.google.com/lakehouse/docs/key-concepts#iceberg-managed-tables)
do receive automated maintenance, but only BigQuery can write to them.

- Partitioned tables are not supported.

- Schema evolution of an Iceberg table is not supported. If the `SINK FROM` object's schema changes, you must drop and recreate the sink.

## Troubleshooting

### Sink creation fails with "input compacted past resume upper"

This error occurs when the source data has been compacted beyond the point where
the sink last committed. This can happen after a Materialize backup/restore
operation. You may need to drop and recreate the sink, which will re-snapshot
the entire source relation.

### Commit conflicts

If another process modifies the Iceberg table while Materialize is committing,
you may see commit conflict errors. Materialize will automatically retry, but
if conflicts persist, ensure no other writers are modifying the same table.

## Related pages

- [`CREATE SINK`](/sql/create-sink/iceberg)
- [`CREATE CONNECTION`](/sql/create-connection)
- [Apache Iceberg documentation](https://iceberg.apache.org/docs/latest/)

---

## Kafka and Redpanda

<!-- Ported over content from sink-kafka.md. -->

## Connectors

Materialize bundles a **native connector** that allow writing data to Kafka and
Redpanda. When a user defines a sink to Kafka/Redpanda, Materialize
automatically generates the required schema and writes down the stream of
changes to that view or source. In effect, Materialize sinks act as change data
capture (CDC) producers for the given source or view.

For details on the connector, including syntax, supported formats and examples,
refer to [`CREATE SINK`](/sql/create-sink/kafka).

> **Tip:** Redpanda uses the same syntax as Kafka [`CREATE SINK`](/sql/create-sink/kafka).

## Features

### Memory use during creation

During creation, sinks need to load an entire snapshot of the data in memory.

### Automatic topic creation

If the specified Kafka topic does not exist, Materialize will attempt to create
it using the broker's default number of partitions, default replication factor,
default compaction policy, and default retention policy, unless any specific
overrides are provided as part of the [connection
options](/sql/create-sink/kafka#syntax).

If the connection's [progress
topic](/sql/create-sink/kafka#exactly-once-processing) does not exist,
Materialize will attempt to create it with a single partition, the broker's
default replication factor, compaction enabled, and both size- and time-based
retention disabled. The replication factor can be overridden using the `PROGRESS
TOPIC REPLICATION FACTOR` option when creating a connection [`CREATE
CONNECTION`](/sql/create-connection).

To customize topic-level configuration, including compaction settings and other
values, use the `TOPIC CONFIG` option in the [connection
options](/sql/create-sink/kafka#syntax) to set any relevant kafka
[topic configs](https://kafka.apache.org/documentation/#topicconfigs).

If you manually create the topic or progress topic in Kafka before
running `CREATE SINK`, observe the following guidance:

| Topic          | Configuration       | Guidance
|----------------|---------------------|---------
| Data topic     | Partition count     | Your choice, based on your performance and ordering requirements.
| Data topic     | Replication factor  | Your choice, based on your durability requirements.
| Data topic     | Compaction          | Your choice, based on your downstream applications' requirements. If using the [Upsert envelope](/sql/create-sink/kafka#upsert), enabling compaction is typically the right choice.
| Data topic     | Retention           | Your choice, based on your downstream applications' requirements.
| Progress topic | Partition count     | **Must be set to 1.** Using multiple partitions can cause Materialize to violate its [exactly-once guarantees](/sql/create-sink/kafka#exactly-once-processing).
| Progress topic | Replication factor  | Your choice, based on your durability requirements.
| Progress topic | Compaction          | We recommend enabling compaction to avoid accumulating unbounded state. Disabling compaction may cause performance issues, but will not cause correctness issues.
| Progress topic | Retention           | **Must be disabled.** Enabling retention can cause Materialize to violate its [exactly-once guarantees](/sql/create-sink/kafka#exactly-once-processing).
| Progress topic | Tiered storage      | We recommend disabling tiered storage to allow for more aggressive data compaction. Fully compacted data requires minimal storage, typically only tens of bytes per sink, making it cost-effective to maintain directly on local disk.
| Progress topic | Segment bytes       | Defaults to 128 MiB. We recommend going no higher than 256 MiB to avoid slow startups when creating new sinks, as they must process the entire progress topic on startup.
> **Warning:** Dropping a Kafka sink doesn't drop the corresponding topic. For more information, see the [Kafka documentation](https://kafka.apache.org/documentation/).

### Exactly-once processing

By default, Kafka sinks provide [exactly-once processing guarantees](https://kafka.apache.org/documentation/#semantics), which ensures that messages are not duplicated or dropped in failure scenarios.

To achieve this, Materialize stores some internal metadata in an additional
*progress topic*. This topic is shared among all sinks that use a particular
[Kafka connection](/sql/create-connection/#kafka). The name of the progress
topic can be specified when [creating a
connection](/sql/create-connection/#kafka); otherwise, a default name of
`_materialize-progress-{REGION ID}-{CONNECTION ID}` is used. In either case,
Materialize will attempt to create the topic if it does not exist. The contents
of this topic are not user-specified.

#### End-to-end exactly-once processing

Exactly-once semantics are an end-to-end property of a system, but Materialize
only controls the initial produce step. To ensure _end-to-end_ exactly-once
message delivery, you should ensure that:

- The broker is configured with replication factor greater than 3, with unclean
  leader election disabled (`unclean.leader.election.enable=false`).
- All downstream consumers are configured to only read committed data
  (`isolation.level=read_committed`).
- The consumers' processing is idempotent, and offsets are only committed when
  processing is complete.

For more details, see [the Kafka documentation](https://kafka.apache.org/documentation/).

### Partitioning

By default, Materialize assigns a partition to each message using the following
strategy:

  1. Encode the message's key in the specified format.
  2. If the format uses a schema registry (Confluent or AWS Glue), strip out
     the header carrying the schema ID from the encoded bytes.
  3. Hash the remaining encoded bytes using [SeaHash].
  4. Divide the hash value by the topic's partition count and assign the
     remainder as the message's partition.

If a message has no key, all messages are sent to partition 0.

To configure a custom partitioning strategy, you can use the `PARTITION BY`
option. This option allows you to specify a SQL expression that computes a hash
for each message, which determines what partition to assign to the message:

```sql
-- General syntax.
CREATE SINK ... INTO KAFKA CONNECTION <name> (PARTITION BY = <expression>) ...;

-- Example.
CREATE SINK ... INTO KAFKA CONNECTION <name> (
    PARTITION BY = kafka_murmur2(name || address)
) ...;
```

The expression:
  * Must have a type that can be assignment cast to [`uint8`].
  * Can refer to any column in the sink's underlying relation when using the
    [upsert envelope](/sql/create-sink/kafka#upsert-envelope).
  * Can refer to any column in the sink's key when using the
    [Debezium envelope](/sql/create-sink/kafka#debezium-envelope).

Materialize uses the computed hash value to assign a partition to each message
as follows:

  1. If the hash is `NULL` or computing the hash produces an error, assign
     partition 0.
  2. Otherwise, divide the hash value by the topic's partition count and assign
     the remainder as the message's partition (i.e., `partition_id = hash %
     partition_count`).

Materialize provides several [hash functions](/sql/functions/#hash-functions)
which are commonly used in Kafka partition assignment:

  * `crc32`
  * `kafka_murmur2`
  * `seahash`

For a full example of using the `PARTITION BY` option, see [Custom
partioning](/sql/create-sink/kafka#custom-partitioning).

### Kafka transaction markers

Materialize uses [Kafka
transactions](https://www.confluent.io/blog/transactions-apache-kafka/). When
Kafka transactions are used, special control messages known as **transaction
markers** are published to the topic. Transaction markers inform both the broker
and clients about the status of a transaction. When a topic is read using a
standard Kafka consumer, these markers are not exposed to the application, which
can give the impression that some offsets are being skipped.

---

## OpenSearch

This guide shows how to send results from Materialize to OpenSearch. A
[Kafka sink](/sql/create-sink/kafka/) writes the results to a Kafka topic.
Kafka Connect reads that topic and writes the documents to OpenSearch.

Use this pipeline to keep an OpenSearch search index up to date to within
hundreds of milliseconds, just using SQL. Materialize maintains the search
document as an incrementally updated view over your operational data, and
pushes precise deltas to OpenSearch as upstream data changes, so only the
affected documents are rewritten.

In this guide, we also use
[`perfect-embedding`](https://github.com/MaterializeInc/perfect-embedding), a
Kafka Connect SMT (single message transform) that we developed.
`perfect-embedding` runs inside the connector and compares the `before` and
`after` values of each change to find the columns that actually changed. It
recomputes a vector embedding only for those columns, so embedding costs scale
with what changed rather than with how often the pipeline runs.

## Before you begin

- An OpenSearch 2.x or later cluster. You install version 4 of the [Aiven
  OpenSearch Sink
  Connector](https://github.com/Aiven-Open/opensearch-connector-for-apache-kafka)
  in Step 3. This connector version does not work with OpenSearch 1.x.

- Kafka Connect workers that run in distributed mode. Each worker needs a
  writable `plugin.path`. The connector requires Java 21 or later on each
  worker.

- Credentials for the connector. Choose one of these methods: basic
  authentication with an internal user under fine-grained access control,
  SigV4, or mTLS.

- A Kafka or Redpanda cluster. Materialize and the destination system must
  both connect to this cluster.

- A materialized view, source, or table to export. A sink cannot read
  from a plain view.

- A cluster to run the sink. Name this cluster with `IN CLUSTER`. See
  [`CREATE CLUSTER`](/sql/create-cluster/). When a sink starts, it loads a
  full snapshot of the relation into memory. Size the cluster for the
  snapshot, not for the steady-state rate of change.

- The [Kafka ACLs](/sql/create-sink/kafka/#required-kafka-acls) that the sink
  needs.

You also need these privileges in Materialize:

- `CREATE` privileges on the containing schema.
- `SELECT` privileges on the item being written out to an external system.
  - NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to
    execute the view definition.
- `CREATE` privileges on the containing cluster if the sink is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the sink is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the sink definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Step 1. Set up the sink in Materialize

The examples in this guide build a search document for an article catalog tracking its content and page views.

### Create the connections

```mzsql
CREATE SECRET kafka_password AS '<BROKER_PASSWORD>';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER '<BROKER_HOST>:9092',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = '<BROKER_USERNAME>',
    SASL PASSWORD = SECRET kafka_password
);

CREATE SECRET csr_password AS '<CSR_PASSWORD>';

CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
    URL '<CSR_URL>',
    USERNAME = '<CSR_USERNAME>',
    PASSWORD = SECRET csr_password
);
```

The embedding transform compares structured records to find changes, so this
pipeline needs Avro with a schema registry. For other authentication
methods, see [`CREATE CONNECTION`](/sql/create-connection/#kafka).

### Create the search document

Create a [materialized view](/sql/create-materialized-view/) that builds the
document you want to search.

```mzsql
CREATE MATERIALIZED VIEW articles AS
    SELECT a.id, a.title, a.body, count(p.article_id) AS views
    FROM article_content a
    LEFT JOIN page_views p ON a.id = p.article_id
    GROUP BY 1, 2, 3;
```

### Create the sink

```mzsql
CREATE SINK articles_sink_v1
  IN CLUSTER sinks_cluster
  FROM articles
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'articles_v1',
    TOPIC PARTITION COUNT 6
  )
  KEY (id) NOT ENFORCED
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE DEBEZIUM;
```

`ENVELOPE DEBEZIUM` wraps each change in a `{"before": ..., "after": ...}`
value. The transform compares these two fields to find the columns that
changed. The transform also converts each delete into a tombstone. The
connector applies this tombstone as a document delete. For the full list of
options, see [`CREATE SINK ... INTO KAFKA`](/sql/create-sink/kafka/).

## Step 2. Create the OpenSearch index

The connector writes documents to an index. The index name is the Kafka
topic name in lowercase letters. The sink topic is `articles_v1`, so the
index name is also `articles_v1`.

Create an empty index named `articles_v1`. The sink fills this index later.

An index that holds vectors needs the `index.knn` setting and an explicit
mapping. The connector sets **neither** of these. An index that the
connector creates cannot serve vector queries.

```nofmt
PUT /articles_v1
{
  "settings": { "index.knn": true },
  "mappings": {
    "properties": {
      "id":    { "type": "integer" },
      "title": { "type": "text" },
      "body":  { "type": "text" },
      "views": { "type": "long" },
      "title_embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "space_type": "cosinesimil",
        "method": { "name": "hnsw" }
      },
      "body_embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "space_type": "cosinesimil",
        "method": { "name": "hnsw" }
      }
    }
  }
}
```

The output should resemble the following:

```nofmt
{ "acknowledged": true, "shards_acknowledged": true, "index": "articles_v1" }
```

For the list of vector options, see OpenSearch's [`knn_vector` field
reference](https://docs.opensearch.org/latest/mappings/supported-field-types/knn-vector/).

Create a read alias named `articles`. Applications send queries to this
alias, not to the index `articles_v1` directly:

```nofmt
POST /_aliases
{
  "actions": [
    { "add": { "index": "articles_v1", "alias": "articles" } }
  ]
}
```

The output should resemble the following:

```nofmt
{ "acknowledged": true }
```

> **Warning:** A new sink's snapshot inserts only the rows that exist when it starts. The
> snapshot does not remove old documents from the destination.
> Do not point a new sink at a destination that already holds documents. Those
> documents stay in the destination. No later write removes them.

## Step 3. Deploy the connector

1. Extract the [Aiven OpenSearch Sink
   Connector](https://github.com/Aiven-Open/opensearch-connector-for-apache-kafka)
   release zip file onto the worker's `plugin.path`. This connector is not
   available on Confluent Hub.
1. Extract the
   [`perfect-embedding`](https://github.com/MaterializeInc/perfect-embedding/releases)
   release zip file into a separate directory on the same `plugin.path`.
1. Restart the workers. Kafka Connect then finds both plugins.

Create the connector. Send this configuration to the Kafka Connect REST API
with `POST /connectors`:

```json
{
  "name": "opensearch-articles",
  "config": {
    "connector.class": "io.aiven.kafka.connect.opensearch.OpenSearchSinkConnector",
    "topics": "articles_v1",
    "connection.url": "https://<OPENSEARCH_HOST>:9200",
    "connection.username": "<OPENSEARCH_USERNAME>",
    "connection.password": "<OPENSEARCH_PASSWORD>",
    "tasks.max": "4",
    "key.ignore": "false",
    "schema.ignore": "false",
    "index.write.method": "upsert",
    "behavior.on.null.values": "delete",
    "behavior.on.version.conflict": "ignore",
    "max.in.flight.requests": "1",
    "batch.size": "100",
    "consumer.override.isolation.level": "read_committed",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "<CSR_URL>",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "<CSR_URL>",
    "transforms": "extractKey,embed",
    "transforms.extractKey.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    "transforms.extractKey.field": "id",
    "transforms.embed.type": "com.materialize.connect.smt.embedding.EmbeddingDiffTransform",
    "transforms.embed.embedded.columns": "title,body",
    "transforms.embed.provider": "openai",
    "transforms.embed.openai.api.key": "${file:/opt/connect/secrets.properties:openai_api_key}",
    "transforms.embed.openai.model": "text-embedding-3-small",
    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "dlq.opensearch.articles_v1",
    "errors.deadletterqueue.context.headers.enable": "true"
  }
}
```

The `${file:...}` reference needs the file config provider. Enable this
provider in the worker properties. Set `config.providers=file` and
`config.providers.file.class=org.apache.kafka.common.config.provider.FileConfigProvider`.

The `embed` transform updates the vectors. For each record, it reads the
Debezium `before` and `after` values. It recomputes an embedding only for a
column in `embedded.columns` whose value changed. It leaves the rest of the
document unchanged:

- `transforms.embed.embedded.columns` names the text columns to embed. Each
  column must have the string type.
- `transforms.embed.provider` selects the embedding provider. This example
  uses `openai`.
- `transforms.embed.openai.api.key` and `transforms.embed.openai.model`
  configure the OpenAI client. The connector reads these settings only when
  `provider` is `openai`.

For the other transform options, see the
[`perfect-embedding`](https://github.com/MaterializeInc/perfect-embedding)
documentation.

## Step 4. Validate the pipeline

1.  Check that the connector is running:

    ```nofmt
    GET /connectors/opensearch-articles/status
    ```

    The output should resemble the following:

    ```nofmt
    {
      "name": "opensearch-articles",
      "connector": { "state": "RUNNING" },
      "tasks": [ { "id": 0, "state": "RUNNING" } ]
    }
    ```

1.  Confirm that the documents have their vectors:

    ```nofmt
    GET /articles/_search
    {
      "size": 1,
      "_source": [ "id", "title", "views", "title_embedding" ]
    }
    ```

    The output should resemble the following:

    ```nofmt
    "hits": [
      {
        "_id": "1",
        "_source": {
          "id": 1,
          "title": "Storage engines",
          "views": 42,
          "title_embedding": [ 0.021, -0.118, ... ]
        }
      }
    ]
    ```

1.  Delete the row with `id = 1` from `article_content` in Materialize:

    ```mzsql
    DELETE FROM article_content WHERE id = 1;
    ```

    Confirm that the document is gone:

    ```nofmt
    GET /articles/_doc/1
    ```

    The response reports `"found": false`.

## Related pages

- [`CREATE SINK ... INTO KAFKA`](/sql/create-sink/kafka/)
- [`CREATE CONNECTION`](/sql/create-connection/#kafka)
- [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/)
- [Sinks](/concepts/sinks/)
- [Kafka and Redpanda](/serve-results/sink/kafka/)
- [Troubleshooting sinks](/serve-results/sink/sink-troubleshooting/)

---

## S3 Compatible Object Storage

This guide walks you through the steps required to export results from
Materialize to an S3 compatible object storage service, such as Google
Cloud Storage, or Cloudflare R2.

## Before you begin:
- Make sure that you have setup your bucket.
- Obtain the following for your bucket. Instructions to obtain these vary by provider.
  - The S3 compatible URI (`S3_BUCKET_URI`)
    - GCS compatible URIs (beginning with `gs://`) are also valid.
  - The S3 compatible access tokens (`ACCESS_KEY_ID` and `SECRET_ACCESS_KEY`)

## Step 1. Create a connection

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, create an [AWS connection](/sql/create-connection/#aws),
   replacing `<ACCESS_KEY_ID>` and  `<SECRET_ACCESS_KEY>` with the credentials for your bucket. The AWS
   connection can be used to connect to any S3 compatible object storage service, by specifying the endpoint and the region.

   For example, to connect to Google Cloud Storage, you can run the following:

    ```mzsql
    CREATE SECRET secret_access_key AS '<SECRET_ACCESS_KEY>';
    CREATE CONNECTION bucket_connection TO AWS (
        ACCESS KEY ID = '<ACCESS_KEY_ID>',
        SECRET ACCESS KEY = SECRET secret_access_key,
        ENDPOINT = 'https://storage.googleapis.com',
        REGION = 'us'
    );
    ```

> **Warning:** `VALIDATE CONNECTION` only works for AWS S3 connections. Using `VALIDATE CONNECTION` to test a connection to S3 compatible object storage service will result in an error. However, you can still use the connection to copy data.

## Step 2. Run a bulk export

To export data to your target bucket, use the [`COPY TO`](/sql/copy-to/#copy-to-s3)
command and the AWS connection you created in the previous step. Replace the `<S3_BUCKET_URI>`
with the S3 compatible URI for your target bucket.

**Parquet:**

```mzsql
COPY some_object TO '<S3_BUCKET_URI>'
WITH (
    AWS CONNECTION = bucket_connection,
    FORMAT = 'parquet'
  );
```

For details on the Parquet writer settings Materialize uses, as well as data
type support and conversion, check the [reference documentation](/sql/copy-to/#copy-to-s3-parquet).

**CSV:**

```mzsql
COPY some_object TO '<S3_BUCKET_URI>'
WITH (
    AWS CONNECTION = bucket_connection,
    FORMAT = 'csv'
  );
```

## Step 3. (Optional) Add scheduling

Bulk exports to object storage using the `COPY TO` command are _one-shot_: every time
you want to export results, you must run the command. To automate running bulk
exports on a regular basis, you can set up scheduling, for example using a
simple `cron`-like service or an orchestration platform like Airflow or
Dagster.

---

## Snowflake

[//]: # "TODO(morsapaes) For Kafka users, it's possible to sink data to
Snowflake continuously using the Snowflake connector for Kafka. We should also
document that approach."

> **Public Preview:** This feature is in public preview.

This guide walks you through the steps required to bulk-export results from
Materialize to Snowflake using Amazon S3 as the intermediate object store.

## Before you begin

- Ensure you have access to an AWS account, and permissions to create and manage
  IAM policies and roles. If you're not an account administrator, you will need
  support from one!

- Ensure you have access to a Snowflake account, and are able to connect as a
  user with either the [`ACCOUNTADMIN` role](https://docs.snowflake.com/en/user-guide/security-access-control-considerations#using-the-accountadmin-role),
  or a role with the [global `CREATE INTEGRATION` privilege](https://docs.snowflake.com/en/user-guide/security-access-control-privileges#global-privileges-account-level-privileges).

## Step 1. Set up bulk exports to Amazon S3

Follow the [Amazon S3 integration guide](/serve-results/s3/) to set up an Amazon
S3 bucket that Materialize securely writes data into. This will be your
starting point for bulk-loading Materialize data into Snowflake.

## Step 2. Configure a Snowflake storage integration

### Create an IAM policy

To bulk-load data from an S3 bucket into Snowflake, you must create a new
[IAM policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
that specifies what actions can be performed on the bucket by the Snowflake
importer role. For Snowflake to be able to read data from the bucket, the IAM
policy must allow the following actions:

Action type  | Action name                                                                            | Action description
-------------|----------------------------------------------------------------------------------------|---------------
Write        | [`s3:GetBucketLocation`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLocation.html) | Grants permission to return the region the bucket is hosted in.
Read         | [`s3:GetObject`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html) | Grants permission to retrieve objects from a bucket.
Read        | [`s3:GetObjectVersion`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html)| Grants permission to retrieve a specific version of an object from a bucket.
List        | [`s3:ListBucket`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html)| Grants permission to list some or all of the objects in a bucket.
Write        | [`s3:DeleteObject`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html) | (Optional) Grants permission to remove an object from a bucket.
Write        | [`s3:DeleteObjectVersion`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html) | (Optional) Grants permission to remove a specific version of an object from a bucket.
Write        | [`s3:PutObject`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html) | (Optional) Grants permission to add an object to a bucket.

To create a new IAM policy:

1. Navigate to **AWS Services**, then **AWS IAM**.

1. In the **IAM Dashboard**, click **Policies**, then **Create policy**.

1. For **Policy editor**, choose **JSON**.

1. Copy and paste the policy below into the editor, replacing `<bucket>` with
   the bucket name and `<prefix>` with the folder path prefix.

   ```json
   {
      "Version": "2012-10-17",
      "Statement": [
         {
            "Effect": "Allow",
            "Action": [
               "s3:PutObject",
               "s3:GetObject",
               "s3:GetObjectVersion",
               "s3:DeleteObject",
               "s3:DeleteObjectVersion"
            ],
            "Resource": "arn:aws:s3:::<bucket>/<prefix>/*"
         },
         {
            "Effect": "Allow",
            "Action": [
               "s3:ListBucket",
               "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::<bucket>",
            "Condition": {
               "StringLike": {
                  "s3:prefix": [
                     "<prefix>/*"
                  ]
               }
            }
         }
      ]
   }
   ```

1. Click **Next**.

1. Enter a name for the policy, and click **Create policy**.

### Create an IAM role

Next, you must attach the policy you just created to a Snowflake-specific
[IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html).

1. Navigate to **AWS Services**, then **AWS IAM**.

1. In the **IAM Dashboard**, click **Roles**, then **Create role**.

1. In **Trusted entity type**, select **Account ID**, then **This account**.
   Later, you'll update it with the unique identifier for your Snowflake account.

1. Check the **Require external ID** box. Enter a placeholder **External ID**
   (e.g. 0000). Later, you'll update it with the unique external ID for your
   Snowflake storage integration.

1. Click **Next**.

1. In **Add permissions**, select the IAM policy you created in [Create an IAM policy](#create-an-iam-policy),
   and click **Next**.

1. Enter a name for the role, and click **Create role**.

1. Click **View role** to see the role summary page, and note down the
   role **ARN**. You will need it in the next step to create a Snowflake storage
   integration.

### Create a Snowflake storage integration

> **Note:** Only users with either the [`ACCOUNTADMIN` role](https://docs.snowflake.com/en/user-guide/security-access-control-considerations#using-the-accountadmin-role),
> or a role with the [global `CREATE INTEGRATION` privilege](https://docs.snowflake.com/en/user-guide/security-access-control-privileges#global-privileges-account-level-privileges)
> can execute this step.

1. In [Snowsight](https://app.snowflake.com/), or your preferred SQL client
connected to Snowflake, create a [storage integration](https://docs.snowflake.com/en/sql-reference/sql/create-storage-integration),
replacing `<role>` with the name of the role you created in the previous step:

   ```sql
   CREATE STORAGE INTEGRATION S3_int
     TYPE = EXTERNAL_STAGE
     STORAGE_PROVIDER = 'S3'
     ENABLED = TRUE
     STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::001234567890:role/<role>'
     STORAGE_ALLOWED_LOCATIONS = ('*');
   ```

1. Retrieve the IAM principal for your Snowflake account using the
   [`DESC INTEGRATION`](https://docs.snowflake.com/en/sql-reference/sql/desc-integration)
   command:

   ```sql
   DESC INTEGRATION s3_int;
   ```

   Note down the values for the `STORAGE_AWS_IAM_USER_ARN` and
   `STORAGE_AWS_EXTERNAL_ID` properties. You will need them in the next step to
   update the Snowflake trust policy attached to your S3 bucket.

### Update the IAM policy

1. In your AWS account, find the IAM role you created in [Create an IAM role](#create-an-iam-role)
   and, under **Trust relationships**, click **Edit trust policy**. Use the values
   for the `STORAGE_AWS_IAM_USER_ARN` and `STORAGE_AWS_EXTERNAL_ID` properties
   from the previous step to update the trust policy's `Principal` and
   `ExternalId`, then click **Update policy**.

## Step 3. Create a Snowflake external stage

Back in Snowflake, create an [external stage](https://docs.snowflake.com/en/user-guide/data-load-S3-create-stage#external-stages) that uses the storage integration above and references your S3 bucket.

```sql
CREATE STAGE s3_stage
  STORAGE_INTEGRATION = s3_int
  URL = 's3://<bucket>/<prefix>/';
```

> **Note:** To create a stage that uses a storage integration, the active user must have a
> role with the [`CREATE STAGE` privilege](https://docs.snowflake.com/en/sql-reference/sql/create-stage)
> for the active schema, as well as the [`USAGE` privilege](https://docs.snowflake.com/en/sql-reference/sql/grant-privilege#syntax)
> on the relevant storage integration.

## Step 4. Import data into Snowflake

To import the data stored in S3 into Snowflake, you can then create a table and
use the [`COPY INTO`](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table)
command to load it from the external stage.

**Parquet:**

Create a table with a single column of type [`VARIANT`](https://docs.snowflake.com/en/sql-reference/data-types-semistructured#variant):

```sql
CREATE TABLE s3_table_parquet (
    col VARIANT
);
```

Use `COPY INTO` to load the data into the table:

```sql
COPY INTO s3_table_parquet
  FROM @S3_stage
  FILE_FORMAT = (TYPE = 'PARQUET');
```

For more details on importing Parquet files staged in S3 into Snowflake, check the
[Snowflake documentation](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table#type-parquet).

**CSV:**

Create a table with the same number of columns as the number of delimited
columns in the input data file:

```sql
CREATE TABLE s3_table_csv (
    col_1 INT,
    col_2 TEXT,
    col_3 TIMESTAMP
);
```

Use `COPY INTO` to load the data into the table:

```sql
COPY INTO s3_table_csv
  FROM @s3_stage
  FILE_FORMAT = (TYPE = 'CSV');
```

For more details on importing CSV files staged in S3 into Snowflake, check the
[Snowflake documentation](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table#type-csv).

## Step 5. (Optional) Add scheduling

Bulk exports to Amazon S3 using the `COPY TO` command are _one-shot_: every time
you want to export results, you must run the command. To automate running bulk
exports from Materialize to Snowflake on a regular basis, you can set up
scheduling, for example using a simple `cron`-like service or an orchestration
platform like Airflow or Dagster.

---

## Troubleshooting sinks

<!-- Copied over from the old manage/troubleshooting guide -->
## Why isn't my sink exporting data?
First, look for errors in [`mz_sink_statuses`](/reference/system-catalog/mz_internal/#mz_sink_statuses):

```mzsql
SELECT * FROM mz_internal.mz_sink_statuses
WHERE name = <SINK_NAME>;
```

If your sink reports a status of `stalled`, you likely have a configuration
issue. The returned `error` field will provide details.

If your sink reports a status of `starting` for more than a few minutes,
[contact support](/support).

## How do I monitor sink ingestion progress?

Repeatedly query the
[`mz_sink_statistics`](/reference/system-catalog/mz_internal/#mz_sink_statistics)
table and look for ingestion statistics that advance over time:

```mzsql
SELECT
    messages_staged,
    messages_committed,
    bytes_staged,
    bytes_committed
FROM mz_internal.mz_sink_statistics
WHERE id = <SINK ID>;
```

(You can also look at statistics for individual worker threads to evaluate
whether ingestion progress is skewed, but it's generally simplest to start
by looking at the aggregate statistics for the whole source.)

The `messages_staged` and `bytes_staged` statistics should roughly correspond
with what materialize has written (but not necessarily committed) to the
external service. For example, the `bytes_staged` and `messages_staged` fields
for a Kafka sink should roughly correspond with how many messages materialize
has written to the Kafka topic, and how big they are (including the key), but
the Kafka transaction for those messages might not have been committed yet.

`messages_committed` and `bytes_committed` correspond to the number of messages
committed to the external service. These numbers can be _smaller_ than the
`*_staged` statistics, because Materialize might fail to write transactions and
retry them.

If any of these statistics are not making progress, your sink might be stalled
or need to be scaled up.

If the `*_staged` statistics are making progress, but the `*_committed` ones
are not, there may be a configuration issues with the external service that is
preventing Materialize from committing transactions. Check the `reason`
column in `mz_sink_statuses`, which can provide more information.

---

## turbopuffer

This guide shows how to send results from Materialize to turbopuffer. A
[Kafka sink](/sql/create-sink/kafka/) writes the results to a Kafka topic.
[`mz-tpuf-sink`](https://github.com/MaterializeInc/mz-turbopuffer-sink)
reads that topic and writes the documents to a turbopuffer namespace.

Use this pipeline to keep a turbopuffer namespace up to date, just using SQL.
Materialize maintains the search document as an incrementally updated view
over your operational data, and pushes precise deltas to turbopuffer as
upstream data changes, so only the affected documents are rewritten.

Vectors come from a **transform**, a Python function that declares the columns
it reads and the attributes it produces. The sink calls a transform only for
the documents whose source columns actually changed, so embedding costs scale
with what changed.

## Before you begin

- A turbopuffer API key, and the region that holds your namespace.

- Python 3.12 or later on the host that runs the sink, and a way to install
  packages. The examples below use [uv](https://docs.astral.sh/uv/).

- Materialize SQL credentials to read catalog metadata.

- A Kafka or Redpanda cluster. Materialize and the destination system must
  both connect to this cluster.

- A materialized view, source, or table to export. A sink cannot read
  from a plain view.

- A cluster to run the sink. Name this cluster with `IN CLUSTER`. See
  [`CREATE CLUSTER`](/sql/create-cluster/). When a sink starts, it loads a
  full snapshot of the relation into memory. Size the cluster for the
  snapshot, not for the steady-state rate of change.

- The [Kafka ACLs](/sql/create-sink/kafka/#required-kafka-acls) that the sink
  needs.

You also need these privileges in Materialize:

- `CREATE` privileges on the containing schema.
- `SELECT` privileges on the item being written out to an external system.
  - NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to
    execute the view definition.
- `CREATE` privileges on the containing cluster if the sink is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the sink is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the sink definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Step 1. Set up the sink in Materialize

The examples in this guide build a search document for an article catalog tracking its content and page views.

### Create the connections

```mzsql
CREATE SECRET kafka_password AS '<BROKER_PASSWORD>';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER '<BROKER_HOST>:9092',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = '<BROKER_USERNAME>',
    SASL PASSWORD = SECRET kafka_password
);

CREATE SECRET csr_password AS '<CSR_PASSWORD>';

CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
    URL '<CSR_URL>',
    USERNAME = '<CSR_USERNAME>',
    PASSWORD = SECRET csr_password
);
```

The embedding transform compares structured records to find changes, so this
pipeline needs Avro with a schema registry. For other authentication
methods, see [`CREATE CONNECTION`](/sql/create-connection/#kafka).

### Create the search document

Create a [materialized view](/sql/create-materialized-view/) that builds the
document you want to search.

```mzsql
CREATE MATERIALIZED VIEW articles AS
    SELECT a.id, a.title, a.body, count(p.article_id) AS views
    FROM article_content a
    LEFT JOIN page_views p ON a.id = p.article_id
    GROUP BY 1, 2, 3;
```

### Create the sink

```mzsql
CREATE SINK articles_sink_v1
  IN CLUSTER sinks_cluster
  FROM articles
  INTO KAFKA CONNECTION kafka_connection (
    TOPIC 'articles_v1',
    TOPIC PARTITION COUNT 6
  )
  KEY (id) NOT ENFORCED
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE DEBEZIUM;
```

`ENVELOPE DEBEZIUM` wraps each change in a `{"before": ..., "after": ...}`
value. The transform compares these two fields to find the columns that
changed. The transform also converts each delete into a tombstone. The
connector applies this tombstone as a document delete. For the full list of
options, see [`CREATE SINK ... INTO KAFKA`](/sql/create-sink/kafka/).

`KEY (id)` must name exactly one column. That column's value becomes the
turbopuffer document id, unchanged. Integer, string, and `uuid` columns work,
and a string id holds at most 64 bytes. To key on something wider, add a
hashed key column to the view and sink that column instead.

## Step 2. Install the sink library

Install `mz-tpuf-sink` and the client for your embedding provider. This
example uses OpenAI:

```sh
uv add "mz-tpuf-sink @ git+https://github.com/MaterializeInc/mz-turbopuffer-sink"
uv add openai
```

## Step 3. Configure and run the sink

The sink writes documents to a turbopuffer namespace. Do not create the
namespace first. turbopuffer creates it on the first write, and the sink
declares the attribute schema on every write. Column types come from the Avro
schema in the schema registry, so numbers stay numbers and timestamps stay
timestamps, filterable and sortable. Adding a column to the view needs no
change to the program below.

> **Warning:** A new sink's snapshot inserts only the rows that exist when it starts. The
> snapshot does not remove old documents from the destination.
> Do not point a new sink at a destination that already holds documents. Those
> documents stay in the destination. No later write removes them.

Write a program that declares the transforms and runs the sink:

```python
import os

from mz_tpuf_sink import FunctionTransform, SinkConfig, run_sink
from openai import OpenAI

client = OpenAI()

def embed_column(column, rows):
    """Embed one column for a batch of documents, in one API call."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[row[column] for row in rows],
    )
    return [{f"{column}_embedding": item.embedding} for item in response.data]

def embedding_transform(column):
    return FunctionTransform(
        name=f"{column}_embedding",
        sources=(column,),
        schema={f"{column}_embedding": {"type": "[1536]f32", "ann": True}},
        distance_metric="cosine_distance",
        batch_size=256,
        compute=lambda rows: embed_column(column, rows),
    )

run_sink(
    SinkConfig(
        kafka_bootstrap_servers="<BROKER_HOST>:9092",
        kafka_topic="articles_v1",
        schema_registry_url="<CSR_URL>",
        schema_registry_auth=f"<CSR_USERNAME>:{os.environ['CSR_PASSWORD']}",
        materialize_dsn=os.environ["MATERIALIZE_DSN"],
        materialize_sink="materialize.public.articles_sink_v1",
        turbopuffer_api_key=os.environ["TURBOPUFFER_API_KEY"],
        turbopuffer_region="aws-us-east-1",
        namespace="articles_v1",
    ),
    transforms=[embedding_transform("title"), embedding_transform("body")],
)
```

The `OpenAI()` client reads its key from the `OPENAI_API_KEY` environment
variable.

Each transform keeps one vector in sync with one text column:

- `sources` names the columns the transform reads. An update that leaves
  every source column unchanged never reaches `compute`. Editing an article's
  `title` re-embeds the title. Changing its `views` a thousand times embeds
  nothing.
- `schema` declares the turbopuffer attributes the transform produces. A
  vector needs `ann: True` and a `distance_metric`, and the sink refuses to
  start without them. A namespace holds at most two vector attributes, so the
  two transforms above are at the limit.
- `batch_size` bounds how many documents reach one `compute` call. The sink
  batches the calls, so one API request covers many documents.
- `distance_metric` applies to the whole namespace. Two vector transforms
  cannot declare different metrics.

A transform is ordinary Python, so it can call any model, local or hosted, and
it can produce anything, not just vectors. A slug, a sentiment score, or a
translated title all work the same way.

`SinkConfig` names the two ends of the pipeline:

- `kafka_topic` is the topic the Materialize sink writes to.
- `materialize_sink` is the sink's fully qualified name, as
  `database.schema.sink`. A bare name could match sinks in several schemas, so
  the sink rejects one.
- `namespace` is the turbopuffer namespace to write.

Run the program:

```sh
uv run python sink.py
```

Run one process per topic, writing to one namespace. `run_sink` blocks until
stopped. To shut down cleanly, pass a `threading.Event` as its second argument
and set that event from a signal handler.

Embedding calls make a flush long-running, and a Kafka consumer that does not
poll within `max.poll.interval.ms` is evicted, which drops buffered state and
replays the work. Raise `kafka_max_poll_interval_ms` in `SinkConfig` if the
sink logs a slow flush warning.

## Step 4. Validate the pipeline

1.  Confirm that the documents arrived with their vectors:

    ```python
    from turbopuffer import Turbopuffer

    namespace = Turbopuffer(
        api_key="<TURBOPUFFER_API_KEY>",
        region="aws-us-east-1",
    ).namespace("articles_v1")

    response = namespace.query(
        rank_by=("id", "asc"),
        top_k=1,
        include_attributes=["id", "title", "views", "title_embedding"],
        consistency={"level": "strong"},
    )
    for row in response.rows:
        print(row.id, row.title, row.views, row.title_embedding[:4])
    ```

    The output should resemble the following:

    ```nofmt
    1 Storage engines 42 [0.021, -0.118, 0.043, 0.009]
    ```

1.  Delete the row with `id = 1` from `article_content` in Materialize:

    ```mzsql
    DELETE FROM article_content WHERE id = 1;
    ```

    Confirm that the document is gone:

    ```python
    response = namespace.query(
        rank_by=("id", "asc"),
        filters=("id", "Eq", 1),
        top_k=1,
        consistency={"level": "strong"},
    )
    print(response.rows)
    ```

    The output is an empty list.

## Related pages

- [`CREATE SINK ... INTO KAFKA`](/sql/create-sink/kafka/)
- [`CREATE CONNECTION`](/sql/create-connection/#kafka)
- [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/)
- [Sinks](/concepts/sinks/)
- [Kafka and Redpanda](/serve-results/sink/kafka/)
- [Troubleshooting sinks](/serve-results/sink/sink-troubleshooting/)

