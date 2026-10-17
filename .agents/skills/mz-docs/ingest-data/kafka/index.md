# Kafka

Connecting Materialize to a Kafka source.

Materialize provides native connector for Kafka message broker. To ingest data
from Kafka, you need to

1. Create a connection that specifies access and authentication parameters.
2. Create a source that specifies the format of the data you want to ingest.

## Supported versions

The Kafka source supports **Kafka 3.2+** and is compatible with most common Kafka hosted services, including all supported versions of the [Confluent Platform](https://docs.confluent.io/platform/current/installation/versions-interoperability.html).

## Formats

Materialize can decode incoming bytes of data from several formats:

- Avro
- JSON
- CSV
- Protobuf
- Plain text
- Raw bytes

## Envelopes

What Materialize actually does with the data it receives depends on the
"envelope" your data provides:

Envelope | Action
---------|-------
**Append-only** | Inserts all received data; does not support updates or deletes.
**Debezium** | Treats data as wrapped in a "diff envelope" that indicates whether the record is an insertion, deletion, or update. The Debezium envelope is only supported by sources published to Kafka by Debezium.<br/><br/>For more information, see [`CREATE SOURCE`: Kafka - Debezium envelope](/sql/create-source/kafka/#debezium-envelope).
**Upsert** | Treats data as having a key and a value. New records with non-null value that have the same key as a preexisting record in the dataflow will replace the preexisting record. New records with null value that have the same key as preexisting record will cause the preexisting record to be deleted. <br/><br/>For more information, see [`CREATE SOURCE`: Kafka - Upsert envelope](/sql/create-source/kafka/#upsert-envelope).

## Integration guides

- [Amazon MSK](/ingest-data/kafka/amazon-msk/)
- [Confluent Cloud](/ingest-data/kafka/confluent-cloud/)
- [Self-hosted Kafka](/ingest-data/kafka/kafka-self-hosted/)
- [Warpstream](/ingest-data/kafka/warpstream/)

## See also

- [Redpanda Cloud](/ingest-data/redpanda/redpanda-cloud/)
- [Redpanda Self-hosted](/ingest-data/redpanda/)

## Pages in this section

- [Amazon Managed Streaming for Apache Kafka (Amazon MSK)](/ingest-data/kafka/amazon-msk/index.md): How to securely connect an Amazon MSK cluster as a source to Materialize.
- [Confluent Cloud](/ingest-data/kafka/confluent-cloud/index.md): How to securely connect a Confluent Cloud Kafka cluster as a source to Materialize.
- [Guide: Handle upstream schema changes with zero downtime](/ingest-data/kafka/source-versioning/index.md): How to handle Kafka topic schema changes on Avro-formatted topics, without any downtime in Materialize
- [Ingest data from Self-hosted Kafka](/ingest-data/kafka/kafka-self-hosted/index.md): How to connect a self-hosted Kafka cluster as a source to Materialize.
- [WarpStream](/ingest-data/kafka/warpstream/index.md): How to securely connect WarpStream to Materialize for efficient data streaming.
