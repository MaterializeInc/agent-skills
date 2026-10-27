# Sink results

Sinking results from Materialize to external systems.

A [sink](/fundamentals/concepts/sinks/) describes the external system you want Materialize to
write data to and details the encoding of that data. You can sink data from a
**materialized** view, a source, or a table.

## Sink methods

To create a sink, you can:

| Method | External system | Guide(s) or Example(s) |
| --- | --- | --- |
| Use <code>COPY TO</code> command | Amazon S3 or S3-compatible storage | <ul> <li><a href="/export-data/s3/" >Sink to Amazon S3</a></li> </ul>  |
| Use Census as an intermediate step | Census supported destinations | <ul> <li><a href="/export-data/census/" >Sink to Census</a></li> </ul>  |
| Use <code>COPY TO</code> S3 or S3-compatible storage as an intermediate step | Snowflake and other systems that can read from S3 | <ul> <li><a href="/export-data/snowflake/" >Sink to Snowflake</a></li> </ul>  |
| Use a native connector | Kafka/Redpanda | <ul> <li><a href="/export-data/kafka/" >Sink to Kafka/Redpanda</a></li> </ul>  |
| Use the Kafka sink + Kafka Connect | Elasticsearch | <ul> <li><a href="/export-data/elasticsearch/" >Sink to Elasticsearch</a></li> </ul>  |
| Use the Kafka sink + Kafka Connect | OpenSearch | <ul> <li><a href="/export-data/opensearch/" >Sink to OpenSearch</a></li> </ul>  |
| Use the Kafka sink + <code>mz-tpuf-sink</code> | turbopuffer | <ul> <li><a href="/export-data/turbopuffer/" >Sink to turbopuffer</a></li> </ul>  |
| Use a native connector | Apache Iceberg hosted on AWS S3 Tables | <ul> <li><a href="/export-data/iceberg/" >Sink to Iceberg</a></li> </ul>  |
| Use <code>SUBSCRIBE</code> | Various | <ul> <li><a href="https://github.com/MaterializeInc/mz-catalog-sync" >Sink to Postgres</a></li> <li><a href="https://github.com/MaterializeIncLabs/mz-redis-sync" >Sink to Redis</a></li> </ul>  |

### Operational guideline

- Avoid putting sinks on the same cluster that hosts sources to allow for
[blue/green deployment](/developer-tools/dbt/blue-green-deployments).

### Troubleshooting

For help, see [Troubleshooting
sinks](/export-data/sink-troubleshooting/).

## Pages in this section

- [Amazon S3](/export-data/s3/index.md): How to export results from Materialize to Amazon S3.
- [Apache Iceberg](/export-data/iceberg/index.md): How to export results from Materialize to Apache Iceberg tables.
- [AWS S3 Tables](/export-data/iceberg-aws/index.md): How to export results from Materialize to Apache Iceberg tables on Amazon S3 Tables.
- [Census](/export-data/census/index.md): How to use Census to export data out of Materialize.
- [Consume from Snowflake on AWS S3 Tables](/export-data/iceberg-aws-snowflake/index.md): How to query Materialize's Iceberg tables on Amazon S3 Tables from Snowflake.
- [Databricks Unity Catalog](/export-data/iceberg-databricks/index.md): How to export results from Materialize to Apache Iceberg tables registered in Databricks Unity Catalog on AWS or Azure.
- [Elasticsearch](/export-data/elasticsearch/index.md): How to export results from Materialize to Elasticsearch using the Kafka sink and Kafka Connect.
- [GCP BigLake](/export-data/iceberg-gcp/index.md): How to export results from Materialize to Apache Iceberg tables on Google Cloud BigLake.
- [Kafka and Redpanda](/export-data/kafka/index.md): How to export results from Materialize to Kafka/Redpanda.
- [OpenSearch](/export-data/opensearch/index.md): How to export results from Materialize to OpenSearch using the Kafka sink and Kafka Connect.
- [S3 Compatible Object Storage](/export-data/s3_compatible/index.md): How to export results from Materialize to S3 compatible object storage
- [Snowflake](/export-data/snowflake/index.md): How to export results from Materialize to Snowflake.
- [Troubleshooting Iceberg sinks](/export-data/iceberg-troubleshooting/index.md): How to diagnose and resolve common issues with Iceberg sinks.
- [Troubleshooting sinks](/export-data/sink-troubleshooting/index.md)
- [turbopuffer](/export-data/turbopuffer/index.md): How to export results from Materialize to turbopuffer using the Kafka sink and mz-tpuf-sink.
- [Understand the lifecycle of a sink](/export-data/lifecycle-of-a-sink/index.md): The states a sink moves through, how to monitor each one, and the error states you might encounter.
