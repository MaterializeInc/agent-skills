# OpenSearch
How to export results from Materialize to OpenSearch using the Kafka sink and Kafka Connect.
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
