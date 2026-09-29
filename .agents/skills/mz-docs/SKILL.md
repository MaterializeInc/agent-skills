---
name: mz-docs
description: Materialize documentation for SQL syntax, data ingestion, concepts, and best practices. Use when users ask about Materialize queries, sources, sinks, views, or clusters.
---

# Materialize Documentation

This skill provides comprehensive documentation for Materialize, a streaming database for real-time analytics.

## How to Use This Skill

When a user asks about Materialize:

1. **For SQL syntax/commands**: Find the `sql` pages in `pages/INDEX.md`
2. **For core concepts**: Find the `fundamentals/concepts` pages in `pages/INDEX.md`
3. **For data ingestion**: Find the `ingest-data` pages in `pages/INDEX.md`
4. **For transformations**: Find the `transform-data` pages in `pages/INDEX.md`

## How the Pages Are Stored

The pages are packed into bundle files under `pages/`. `pages/INDEX.md` lists every page path with its title and bundle. In a bundle, each page starts at a `<!-- mz-docs page: <path> -->` marker, so search the bundle for the marker rather than reading it whole. A link such as `/sql/create-source/kafka/` refers to the page `sql/create-source/kafka`.

## Documentation Sections

### Clusters
Guidance for configuring and operating Materialize clusters.

- **Autoscaling for hydration**: `pages/clusters-01.md` (page `clusters/autoscaling`)
- **M.1 to cc size mapping**: `pages/clusters-01.md` (page `clusters/m1-cc-mapping`)
- **Operational guidelines**: `pages/clusters-01.md` (page `clusters/operational-guidelines`)
- **Optimize hydration requirements**: `pages/clusters-01.md` (page `clusters/optimize-hydration-requirements`)
- **Size clusters for hydration**: `pages/clusters-01.md` (page `clusters/sizing`)
- **System clusters**: `pages/clusters-01.md` (page `clusters/system-clusters`)
- **Troubleshoot clusters**: `pages/clusters-01.md` (page `clusters/troubleshoot-clusters`)

### Developer tools
Tools for developing, deploying, and managing Materialize.

- **Download and run Materialize Emulator**: `pages/developer-tools-01.md` (page `developer-tools/install-materialize-emulator`)
- **Manage Materialize**: `pages/developer-tools-01.md` (page `developer-tools/manage`)
- **Materialize console**: `pages/developer-tools-01.md` (page `developer-tools/console`)
- **MCP Servers and agent skills**: `pages/developer-tools-01.md` (page `developer-tools/mcp-server`)
- **mz-debug**: `pages/developer-tools-01.md` (page `developer-tools/mz-debug`)
- **Tools and integrations**: `pages/developer-tools-01.md` (page `developer-tools/integrations`)
- **Use dbt to manage Materialize**: `pages/developer-tools-01.md` (page `developer-tools/dbt`)
- **Use mz-deploy to manage Materialize**: `pages/developer-tools-01.md` (page `developer-tools/mz-deploy`)
- **Use Terraform to manage Materialize**: `pages/developer-tools-02.md` (page `developer-tools/terraform`)

### Ingest data
Best practices for ingesting data into Materialize from external systems.

- **Amazon EventBridge**: `pages/ingest-data-05.md` (page `ingest-data/webhooks/amazon-eventbridge`)
- **AWS PrivateLink connections (Cloud-only)**: `pages/ingest-data-03.md` (page `ingest-data/network-security/privatelink`)
- **Change a webhook source's included headers**: `pages/ingest-data-05.md` (page `ingest-data/webhooks/change-included-headers`)
- **CockroachDB CDC using Kafka and Changefeeds**: `pages/ingest-data-01.md` (page `ingest-data/cdc-cockroachdb`)
- **Debezium**: `pages/ingest-data-01.md` (page `ingest-data/debezium`)
- **Fivetran**: `pages/ingest-data-01.md` (page `ingest-data/fivetran`)
- **HubSpot**: `pages/ingest-data-05.md` (page `ingest-data/webhooks/hubspot`)
- **Ingestion performance**: `pages/ingest-data-03.md` (page `ingest-data/performance`)
- **Kafka**: `pages/ingest-data-01.md` (page `ingest-data/kafka`)
- **MongoDB**: `pages/ingest-data-01.md` (page `ingest-data/mongodb`)
- _(and 16 more files in this section)_

### Materialize Cloud
Guidance for operating Materialize Cloud.

- **Customer responsibility model (Cloud)**: `pages/materialize-cloud-01.md` (page `materialize-cloud/customer-responsibilities`)
- **Disaster recovery (Cloud)**: `pages/materialize-cloud-01.md` (page `materialize-cloud/disaster-recovery`)
- **Free Trials**: `pages/materialize-cloud-01.md` (page `materialize-cloud/free-trials`)
- **Usage & billing (Cloud)**: `pages/materialize-cloud-01.md` (page `materialize-cloud/billing`)

### Monitoring and alerting
Monitor the performance of your Materialize region with Datadog and Grafana.

- **Appendix: Metrics**: `pages/observability-01.md` (page `observability/appendix-metrics`)
- **Cloud**: `pages/observability-01.md` (page `observability/cloud`)
- **Essential metrics**: `pages/observability-01.md` (page `observability/essential-metrics`)
- **Replica resource usage**: `pages/observability-01.md` (page `observability/replica-resource-usage`)
- **Self-Managed**: `pages/observability-01.md` (page `observability/self-managed`)

### Overview
Learn how to efficiently transform data using Materialize SQL.

- **Dataflow troubleshooting**: `pages/transform-data-01.md` (page `transform-data/dataflow-troubleshooting`)
- **Dictionary compression**: `pages/transform-data-01.md` (page `transform-data/dictionary-compression`)
- **FAQ: Indexes**: `pages/transform-data-01.md` (page `transform-data/faq`)
- **Freshness troubleshooting**: `pages/transform-data-01.md` (page `transform-data/freshness-troubleshooting`)
- **How to monitor freshness in Materialize**: `pages/transform-data-02.md` (page `transform-data/monitor-freshness`)
- **Idiomatic Materialize SQL**: `pages/transform-data-01.md` (page `transform-data/idiomatic-materialize-sql`)
- **Optimization**: `pages/transform-data-02.md` (page `transform-data/optimization`)
- **Patterns**: `pages/transform-data-02.md` (page `transform-data/patterns`)
- **Updating materialized views**: `pages/transform-data-02.md` (page `transform-data/updating-materialized-views`)

### Security

- **Appendix**: `pages/security-01.md` (page `security/appendix`)
- **Cloud**: `pages/security-01.md` (page `security/cloud`)
- **Self-managed**: `pages/security-01.md` (page `security/self-managed`)

### Self-Managed Deployments
Learn about the key components and architecture of self-managed Materialize deployments.

- **Appendix**: `pages/self-managed-deployments-01.md` (page `self-managed-deployments/appendix`)
- **Configuring System Parameters**: `pages/self-managed-deployments-01.md` (page `self-managed-deployments/configuration-system-parameters`)
- **Deployment guidelines**: `pages/self-managed-deployments-01.md` (page `self-managed-deployments/deployment-guidelines`)
- **FAQ**: `pages/self-managed-deployments-01.md` (page `self-managed-deployments/faq`)
- **Installation**: `pages/self-managed-deployments-01.md` (page `self-managed-deployments/installation`)
- **Materialize CRD Field Descriptions**: `pages/self-managed-deployments-01.md` (page `self-managed-deployments/materialize-crd-field-descriptions`)
- **Materialize Operator Configuration**: `pages/self-managed-deployments-02.md` (page `self-managed-deployments/operator-configuration`)
- **Query History**: `pages/self-managed-deployments-02.md` (page `self-managed-deployments/query-history`)
- **Self-managed release versions**: `pages/self-managed-deployments-02.md` (page `self-managed-deployments/release-versions`)
- **Troubleshooting**: `pages/self-managed-deployments-02.md` (page `self-managed-deployments/troubleshooting`)
- _(and 2 more files in this section)_

### Serve results
Serving results from Materialize

- **`SELECT` and `SUBSCRIBE`**: `pages/serve-results-01.md` (page `serve-results/query-results`)
- **ADBC (Arrow Database Connectivity)**: `pages/serve-results-01.md` (page `serve-results/adbc`)
- **Client libraries**: `pages/serve-results-01.md` (page `serve-results/client-libraries`)
- **Connect to Materialize via HTTP**: `pages/serve-results-01.md` (page `serve-results/http-api`)
- **Connect to Materialize via WebSocket**: `pages/serve-results-01.md` (page `serve-results/websocket-api`)
- **Connection Pooling**: `pages/serve-results-01.md` (page `serve-results/connection-pooling`)
- **Durable subscriptions**: `pages/serve-results-01.md` (page `serve-results/durable-subscriptions`)
- **Foreign data wrapper (FDW) **: `pages/serve-results-01.md` (page `serve-results/fdw-setup`)
- **Isolation levels**: `pages/serve-results-01.md` (page `serve-results/isolation-level`)
- **SQL clients**: `pages/serve-results-01.md` (page `serve-results/sql-clients`)
- _(and 3 more files in this section)_

### Sink results
Sinking results from Materialize to external systems.

- **Amazon S3**: `pages/export-data-01.md` (page `export-data/s3`)
- **Apache Iceberg**: `pages/export-data-01.md` (page `export-data/iceberg`)
- **AWS S3 Tables**: `pages/export-data-01.md` (page `export-data/iceberg-aws`)
- **Census**: `pages/export-data-01.md` (page `export-data/census`)
- **Consume from Snowflake on AWS S3 Tables**: `pages/export-data-01.md` (page `export-data/iceberg-aws-snowflake`)
- **Databricks Unity Catalog**: `pages/export-data-01.md` (page `export-data/iceberg-databricks`)
- **Elasticsearch**: `pages/export-data-01.md` (page `export-data/elasticsearch`)
- **GCP BigLake**: `pages/export-data-01.md` (page `export-data/iceberg-gcp`)
- **Kafka and Redpanda**: `pages/export-data-01.md` (page `export-data/kafka`)
- **OpenSearch**: `pages/export-data-01.md` (page `export-data/opensearch`)
- _(and 5 more files in this section)_

### SQL commands
SQL commands reference.

- **Namespaces**: `pages/sql-06.md` (page `sql/namespaces`)
- **ALTER CLUSTER**: `pages/sql-01.md` (page `sql/alter-cluster`)
- **ALTER CLUSTER REPLICA**: `pages/sql-01.md` (page `sql/alter-cluster-replica`)
- **ALTER CONNECTION**: `pages/sql-01.md` (page `sql/alter-connection`)
- **ALTER DATABASE**: `pages/sql-01.md` (page `sql/alter-database`)
- **ALTER DEFAULT PRIVILEGES**: `pages/sql-01.md` (page `sql/alter-default-privileges`)
- **ALTER INDEX**: `pages/sql-01.md` (page `sql/alter-index`)
- **ALTER MATERIALIZED VIEW**: `pages/sql-01.md` (page `sql/alter-materialized-view`)
- **ALTER NETWORK POLICY (Cloud)**: `pages/sql-01.md` (page `sql/alter-network-policy`)
- **ALTER ROLE**: `pages/sql-01.md` (page `sql/alter-role`)
- _(and 111 more files in this section)_

### What is Materialize?
Learn more about Materialize

- **Architecture Patterns**: `pages/fundamentals-01.md` (page `fundamentals/architecture-patterns`)
- **Concepts**: `pages/fundamentals-01.md` (page `fundamentals/concepts`)

## Quick Reference

### Common SQL Commands

| Command | Description |
|---------|-------------|
| `CREATE SOURCE` | Connect to external data sources (Kafka, PostgreSQL, MySQL) |
| `CREATE MATERIALIZED VIEW` | Create incrementally maintained views |
| `CREATE INDEX` | Create indexes on views for faster queries |
| `CREATE SINK` | Export data to external systems |
| `SELECT` | Query data from sources, views, and tables |

### Key Concepts

- **Sources**: Connections to external data systems that stream data into Materialize
- **Materialized Views**: Views that are incrementally maintained as source data changes
- **Indexes**: Arrangements of data in memory for fast point lookups
- **Clusters**: Isolated compute resources for running dataflows
- **Sinks**: Connections that export data from Materialize to external systems
