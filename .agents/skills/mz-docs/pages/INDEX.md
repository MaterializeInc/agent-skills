# mz-docs page index

Each documentation page lives in one bundle file in this directory. In a bundle,
a page starts at its `<!-- mz-docs page: <path> -->` marker. Links inside the
docs such as `/sql/create-source/kafka/` refer to the page with that path.

| Page | Title | Bundle |
|---|---|---|
| `clusters` | Clusters | `clusters-01.md` |
| `clusters/autoscaling` | Autoscaling for hydration | `clusters-01.md` |
| `clusters/m1-cc-mapping` | M.1 to cc size mapping | `clusters-01.md` |
| `clusters/operational-guidelines` | Operational guidelines | `clusters-01.md` |
| `clusters/operational-guidelines/appendix-alternative-cluster-architectures` | Appendix: Alternative cluster architectures | `clusters-01.md` |
| `clusters/optimize-hydration-requirements` | Optimize hydration requirements | `clusters-01.md` |
| `clusters/sizing` | Size clusters for hydration | `clusters-01.md` |
| `clusters/system-clusters` | System clusters | `clusters-01.md` |
| `clusters/troubleshoot-clusters` | Troubleshoot clusters | `clusters-01.md` |
| `clusters/troubleshoot-clusters/cpu-troubleshooting` | Troubleshoot anomalies in CPU usage | `clusters-01.md` |
| `clusters/troubleshoot-clusters/memory-spike` | Troubleshoot anomalies in memory usage | `clusters-01.md` |
| `developer-tools` | Developer tools | `developer-tools-01.md` |
| `developer-tools/console` | Materialize console | `developer-tools-01.md` |
| `developer-tools/console/admin` | Admin (Cloud-only) | `developer-tools-01.md` |
| `developer-tools/console/clusters` | Clusters | `developer-tools-01.md` |
| `developer-tools/console/connect` | Connect (Cloud-only) | `developer-tools-01.md` |
| `developer-tools/console/create-new` | Create new | `developer-tools-01.md` |
| `developer-tools/console/data` | Database object explorer | `developer-tools-01.md` |
| `developer-tools/console/integrations` | Integrations | `developer-tools-01.md` |
| `developer-tools/console/monitoring` | Monitoring | `developer-tools-01.md` |
| `developer-tools/console/sql-shell` | SQL Shell | `developer-tools-01.md` |
| `developer-tools/console/user-profile` | User profile | `developer-tools-01.md` |
| `developer-tools/dbt` | Use dbt to manage Materialize | `developer-tools-01.md` |
| `developer-tools/dbt/blue-green-deployments` | Blue-green deployment | `developer-tools-01.md` |
| `developer-tools/dbt/development-workflows` | Development guidelines | `developer-tools-01.md` |
| `developer-tools/dbt/get-started` | Get started with dbt and Materialize | `developer-tools-01.md` |
| `developer-tools/dbt/slim-deployments` | Slim deployments | `developer-tools-01.md` |
| `developer-tools/install-materialize-emulator` | Download and run Materialize Emulator | `developer-tools-01.md` |
| `developer-tools/integrations` | Tools and integrations | `developer-tools-01.md` |
| `developer-tools/manage` | Manage Materialize | `developer-tools-01.md` |
| `developer-tools/mcp-server` | MCP Servers and agent skills | `developer-tools-01.md` |
| `developer-tools/mcp-server/coding-agent-skills` | Agent Skills | `developer-tools-01.md` |
| `developer-tools/mcp-server/mcp-agent` | MCP Server for Agents | `developer-tools-01.md` |
| `developer-tools/mcp-server/mcp-agent-config` | Agent endpoint configuration | `developer-tools-01.md` |
| `developer-tools/mcp-server/mcp-agent-tools` | Agent MCP server tools | `developer-tools-01.md` |
| `developer-tools/mcp-server/mcp-developer` | MCP Server for Developers and Operators | `developer-tools-01.md` |
| `developer-tools/mcp-server/mcp-developer-config` | Developer endpoint configuration | `developer-tools-01.md` |
| `developer-tools/mcp-server/mcp-developer-tools` | Developer MCP server tools | `developer-tools-01.md` |
| `developer-tools/mcp-server/mcp-server-troubleshooting` | MCP Server Troubleshooting | `developer-tools-01.md` |
| `developer-tools/mz-debug` | mz-debug | `developer-tools-01.md` |
| `developer-tools/mz-debug/emulator` | mz-debug emulator | `developer-tools-01.md` |
| `developer-tools/mz-debug/self-managed` | mz-debug self-managed | `developer-tools-01.md` |
| `developer-tools/mz-deploy` | Use mz-deploy to manage Materialize | `developer-tools-01.md` |
| `developer-tools/mz-deploy/agent-setup` | AI agent setup | `developer-tools-01.md` |
| `developer-tools/mz-deploy/deployments` | Deployments | `developer-tools-01.md` |
| `developer-tools/mz-deploy/editor-setup` | Editor setup | `developer-tools-02.md` |
| `developer-tools/mz-deploy/get-started` | Get started with mz-deploy | `developer-tools-02.md` |
| `developer-tools/mz-deploy/infrastructure` | Infrastructure | `developer-tools-02.md` |
| `developer-tools/mz-deploy/local-development` | Local development | `developer-tools-02.md` |
| `developer-tools/mz-deploy/profiles` | Profiles | `developer-tools-02.md` |
| `developer-tools/mz-deploy/project-structure` | Project structure | `developer-tools-02.md` |
| `developer-tools/mz-deploy/stable-apis` | Stable APIs | `developer-tools-02.md` |
| `developer-tools/terraform` | Use Terraform to manage Materialize | `developer-tools-02.md` |
| `developer-tools/terraform/appendix-secret-stores` | Appendix: External secret stores | `developer-tools-02.md` |
| `developer-tools/terraform/get-started` | Get started with the Materialize provider | `developer-tools-02.md` |
| `developer-tools/terraform/manage-cloud-modules` | Manage cloud resources | `developer-tools-02.md` |
| `developer-tools/terraform/manage-rbac` | Manage privileges | `developer-tools-02.md` |
| `developer-tools/terraform/manage-resources` | Manage Materialize resources with the Materialize provider | `developer-tools-02.md` |
| `export-data` | Sink results | `export-data-01.md` |
| `export-data/build-your-own-sink` | Build your own sink | `export-data-01.md` |
| `export-data/build-your-own-sink/postgres` | PostgreSQL | `export-data-01.md` |
| `export-data/census` | Census | `export-data-01.md` |
| `export-data/elasticsearch` | Elasticsearch | `export-data-01.md` |
| `export-data/iceberg` | Apache Iceberg | `export-data-01.md` |
| `export-data/iceberg-aws` | AWS S3 Tables | `export-data-01.md` |
| `export-data/iceberg-aws-snowflake` | Consume from Snowflake on AWS S3 Tables | `export-data-01.md` |
| `export-data/iceberg-databricks` | Databricks Unity Catalog | `export-data-01.md` |
| `export-data/iceberg-gcp` | GCP BigLake | `export-data-01.md` |
| `export-data/kafka` | Kafka and Redpanda | `export-data-01.md` |
| `export-data/lifecycle-of-a-sink` | Understand the lifecycle of a sink | `export-data-01.md` |
| `export-data/opensearch` | OpenSearch | `export-data-01.md` |
| `export-data/s3` | Amazon S3 | `export-data-01.md` |
| `export-data/s3_compatible` | S3 Compatible Object Storage | `export-data-01.md` |
| `export-data/sink-troubleshooting` | Troubleshooting sinks | `export-data-01.md` |
| `export-data/snowflake` | Snowflake | `export-data-01.md` |
| `export-data/turbopuffer` | turbopuffer | `export-data-01.md` |
| `fundamentals` | What is Materialize? | `fundamentals-01.md` |
| `fundamentals/architecture-patterns` | Architecture Patterns | `fundamentals-01.md` |
| `fundamentals/architecture-patterns/live-context-graph` | Live Context Graph | `fundamentals-01.md` |
| `fundamentals/concepts` | Concepts | `fundamentals-01.md` |
| `fundamentals/concepts/arrangements` | Arrangements | `fundamentals-01.md` |
| `fundamentals/concepts/clusters` | Clusters | `fundamentals-01.md` |
| `fundamentals/concepts/hydration` | Hydration | `fundamentals-01.md` |
| `fundamentals/concepts/indexes` | Indexes | `fundamentals-01.md` |
| `fundamentals/concepts/namespaces` | Namespaces | `fundamentals-01.md` |
| `fundamentals/concepts/reaction-time` | Reaction Time, Freshness, and Query Latency | `fundamentals-01.md` |
| `fundamentals/concepts/sinks` | Sinks | `fundamentals-01.md` |
| `fundamentals/concepts/snapshotting` | Snapshotting | `fundamentals-01.md` |
| `fundamentals/concepts/sources` | Sources | `fundamentals-01.md` |
| `fundamentals/concepts/views` | Views | `fundamentals-01.md` |
| `get-started` | Getting started with Materialize | `get-started-01.md` |
| `ingest-data` | Ingest data | `ingest-data-01.md` |
| `ingest-data/cdc-cockroachdb` | CockroachDB CDC using Kafka and Changefeeds | `ingest-data-01.md` |
| `ingest-data/debezium` | Debezium | `ingest-data-01.md` |
| `ingest-data/fivetran` | Fivetran | `ingest-data-01.md` |
| `ingest-data/kafka` | Kafka | `ingest-data-01.md` |
| `ingest-data/kafka/amazon-msk` | Amazon Managed Streaming for Apache Kafka (Amazon MSK) | `ingest-data-01.md` |
| `ingest-data/kafka/confluent-cloud` | Confluent Cloud | `ingest-data-01.md` |
| `ingest-data/kafka/kafka-self-hosted` | Ingest data from Self-hosted Kafka | `ingest-data-01.md` |
| `ingest-data/kafka/source-versioning` | Guide: Handle upstream schema changes with zero downtime | `ingest-data-01.md` |
| `ingest-data/kafka/warpstream` | WarpStream | `ingest-data-01.md` |
| `ingest-data/lifecycle-of-a-source` | Understand the lifecycle of a source | `ingest-data-01.md` |
| `ingest-data/mongodb` | MongoDB | `ingest-data-01.md` |
| `ingest-data/monitoring-data-ingestion` | Monitoring data ingestion | `ingest-data-01.md` |
| `ingest-data/mysql` | MySQL | `ingest-data-01.md` |
| `ingest-data/mysql/amazon-aurora` | Ingest data from Amazon Aurora | `ingest-data-02.md` |
| `ingest-data/mysql/amazon-rds` | Ingest data from Amazon RDS | `ingest-data-02.md` |
| `ingest-data/mysql/azure-db` | Ingest data from Azure DB | `ingest-data-02.md` |
| `ingest-data/mysql/google-cloud-sql` | Ingest data from Google Cloud SQL | `ingest-data-02.md` |
| `ingest-data/mysql/mysql-debezium` | MySQL CDC using Kafka and Debezium | `ingest-data-02.md` |
| `ingest-data/mysql/received-out-of-order-gtids` | Troubleshooting: Received out of order GTIDs | `ingest-data-02.md` |
| `ingest-data/mysql/self-hosted` | Ingest data from self-hosted MySQL | `ingest-data-02.md` |
| `ingest-data/mysql/snapshot-parallelism` | Snapshot parallelism | `ingest-data-02.md` |
| `ingest-data/mysql/source-versioning` | Handle upstream schema changes | `ingest-data-02.md` |
| `ingest-data/mysql/troubleshooting` | Troubleshooting | `ingest-data-02.md` |
| `ingest-data/network-security/privatelink` | AWS PrivateLink connections (Cloud-only) | `ingest-data-03.md` |
| `ingest-data/network-security/ssh-tunnel` | SSH tunnel connections | `ingest-data-03.md` |
| `ingest-data/network-security/static-ips` | Static IP addresses (Cloud-only) | `ingest-data-03.md` |
| `ingest-data/patterns` | Patterns | `ingest-data-03.md` |
| `ingest-data/patterns/upstream-schema-changes` | Absorbing upstream schema changes | `ingest-data-03.md` |
| `ingest-data/performance` | Ingestion performance | `ingest-data-03.md` |
| `ingest-data/postgres` | PostgreSQL | `ingest-data-03.md` |
| `ingest-data/postgres/alloydb` | Ingest data from AlloyDB | `ingest-data-03.md` |
| `ingest-data/postgres/amazon-aurora` | Ingest data from Amazon Aurora | `ingest-data-03.md` |
| `ingest-data/postgres/amazon-rds` | Ingest data from Amazon RDS | `ingest-data-04.md` |
| `ingest-data/postgres/azure-db` | Ingest data from Azure DB | `ingest-data-04.md` |
| `ingest-data/postgres/cloud-sql` | Ingest data from Google Cloud SQL | `ingest-data-04.md` |
| `ingest-data/postgres/connection-closed` | Troubleshooting: Connection closed | `ingest-data-04.md` |
| `ingest-data/postgres/faq` | FAQ: PostgreSQL sources | `ingest-data-04.md` |
| `ingest-data/postgres/logical-replica` | Guide: Ingest from a dedicated PostgreSQL replica | `ingest-data-04.md` |
| `ingest-data/postgres/major-version-upgrade` | Guide: Upgrade the major version of your PostgreSQL source | `ingest-data-04.md` |
| `ingest-data/postgres/neon` | Ingest data from Neon | `ingest-data-04.md` |
| `ingest-data/postgres/partitioned-tables` | Guide: Ingest from partitioned tables | `ingest-data-04.md` |
| `ingest-data/postgres/postgres-debezium` | PostgreSQL CDC using Kafka and Debezium | `ingest-data-04.md` |
| `ingest-data/postgres/replication-slot-active` | Troubleshooting: Replication slot is active | `ingest-data-05.md` |
| `ingest-data/postgres/self-hosted` | Ingest data from self-hosted PostgreSQL | `ingest-data-05.md` |
| `ingest-data/postgres/slot-overcompacted` | Troubleshooting: Slot overcompacted | `ingest-data-05.md` |
| `ingest-data/postgres/source-versioning` | Handle upstream schema changes | `ingest-data-05.md` |
| `ingest-data/postgres/troubleshooting` | Troubleshooting | `ingest-data-05.md` |
| `ingest-data/redpanda` | Redpanda | `ingest-data-05.md` |
| `ingest-data/redpanda/redpanda-cloud` | Redpanda Cloud | `ingest-data-05.md` |
| `ingest-data/sql-server` | SQL Server | `ingest-data-05.md` |
| `ingest-data/sql-server/azure-db` | Ingest data from Azure SQL Database | `ingest-data-05.md` |
| `ingest-data/sql-server/self-hosted` | Ingest data from self-hosted SQL Server | `ingest-data-05.md` |
| `ingest-data/sql-server/source-versioning` | Handle upstream schema changes | `ingest-data-05.md` |
| `ingest-data/striim` | Striim Cloud | `ingest-data-05.md` |
| `ingest-data/troubleshooting` | Troubleshooting | `ingest-data-05.md` |
| `ingest-data/webhooks/amazon-eventbridge` | Amazon EventBridge | `ingest-data-05.md` |
| `ingest-data/webhooks/change-included-headers` | Change a webhook source's included headers | `ingest-data-05.md` |
| `ingest-data/webhooks/hubspot` | HubSpot | `ingest-data-05.md` |
| `ingest-data/webhooks/rudderstack` | RudderStack | `ingest-data-05.md` |
| `ingest-data/webhooks/segment` | Segment | `ingest-data-06.md` |
| `ingest-data/webhooks/snowcatcloud` | SnowcatCloud | `ingest-data-06.md` |
| `ingest-data/webhooks/stripe` | Stripe | `ingest-data-06.md` |
| `ingest-data/webhooks/webhook-quickstart` | Webhooks quickstart | `ingest-data-06.md` |
| `license` | License | `license-01.md` |
| `materialize-cloud` | Materialize Cloud | `materialize-cloud-01.md` |
| `materialize-cloud/billing` | Usage & billing (Cloud) | `materialize-cloud-01.md` |
| `materialize-cloud/customer-responsibilities` | Customer responsibility model (Cloud) | `materialize-cloud-01.md` |
| `materialize-cloud/disaster-recovery` | Disaster recovery (Cloud) | `materialize-cloud-01.md` |
| `materialize-cloud/disaster-recovery/recovery-characteristics` | Materialize Cloud DR characteristics | `materialize-cloud-01.md` |
| `materialize-cloud/free-trials` | Free Trials | `materialize-cloud-01.md` |
| `observability` | Monitoring and alerting | `observability-01.md` |
| `observability/appendix-metrics` | Appendix: Metrics | `observability-01.md` |
| `observability/cloud` | Cloud | `observability-01.md` |
| `observability/cloud/alerting` | Alerting | `observability-01.md` |
| `observability/cloud/datadog` | Datadog | `observability-01.md` |
| `observability/cloud/grafana` | Grafana | `observability-01.md` |
| `observability/essential-metrics` | Essential metrics | `observability-01.md` |
| `observability/replica-resource-usage` | Replica resource usage | `observability-01.md` |
| `observability/self-managed` | Self-Managed | `observability-01.md` |
| `observability/self-managed/alerting` | Alerting | `observability-01.md` |
| `observability/self-managed/datadog` | Datadog | `observability-02.md` |
| `observability/self-managed/google-cloud-monitoring` | Google Cloud Monitoring | `observability-02.md` |
| `observability/self-managed/grafana` | Grafana | `observability-02.md` |
| `observability/self-managed/honeycomb` | Honeycomb | `observability-02.md` |
| `observability/self-managed/opentelemetry` | OpenTelemetry | `observability-02.md` |
| `observability/self-managed/prometheus-remote-write` | Prometheus remote write | `observability-02.md` |
| `observability/self-managed/storage` | How logs and metrics are stored and delivered | `observability-02.md` |
| `releases` | Releases | `releases-01.md` |
| `releases/schedule` | Release Schedule | `releases-01.md` |
| `releases/v0.100` | Materialize v0.100 | `releases-01.md` |
| `releases/v0.101` | Materialize v0.101 | `releases-01.md` |
| `releases/v0.106` | Materialize v0.106 | `releases-01.md` |
| `releases/v0.107` | Materialize v0.107 | `releases-01.md` |
| `releases/v0.108` | Materialize v0.108 | `releases-01.md` |
| `releases/v0.27` | Materialize v0.27 | `releases-01.md` |
| `releases/v0.28` | Materialize v0.28 | `releases-01.md` |
| `releases/v0.29` | Materialize v0.29 | `releases-01.md` |
| `releases/v0.30` | Materialize v0.30 | `releases-01.md` |
| `releases/v0.31` | Materialize v0.31 | `releases-01.md` |
| `releases/v0.32` | Materialize v0.32 | `releases-01.md` |
| `releases/v0.33` | Materialize v0.33 | `releases-01.md` |
| `releases/v0.36` | Materialize v0.36 | `releases-01.md` |
| `releases/v0.37` | Materialize v0.37 | `releases-01.md` |
| `releases/v0.38` | Materialize v0.38 | `releases-01.md` |
| `releases/v0.39` | Materialize v0.39 | `releases-01.md` |
| `releases/v0.40` | Materialize v0.40 | `releases-01.md` |
| `releases/v0.41` | Materialize v0.41 | `releases-01.md` |
| `releases/v0.42` | Materialize v0.42 | `releases-01.md` |
| `releases/v0.43` | Materialize v0.43 | `releases-01.md` |
| `releases/v0.44` | Materialize v0.44 | `releases-01.md` |
| `releases/v0.45` | Materialize v0.45 | `releases-01.md` |
| `releases/v0.46` | Materialize v0.46 | `releases-01.md` |
| `releases/v0.47` | Materialize v0.47 | `releases-01.md` |
| `releases/v0.48` | Materialize v0.48 | `releases-01.md` |
| `releases/v0.49` | Materialize v0.49 | `releases-02.md` |
| `releases/v0.50` | Materialize v0.50 | `releases-02.md` |
| `releases/v0.51` | Materialize v0.51 | `releases-02.md` |
| `releases/v0.52` | Materialize v0.52 | `releases-02.md` |
| `releases/v0.53` | Materialize v0.53 | `releases-02.md` |
| `releases/v0.54` | Materialize v0.54 | `releases-02.md` |
| `releases/v0.55` | Materialize v0.55 | `releases-02.md` |
| `releases/v0.56` | Materialize v0.56 | `releases-02.md` |
| `releases/v0.57` | Materialize v0.57 | `releases-02.md` |
| `releases/v0.58` | Materialize v0.58 | `releases-02.md` |
| `releases/v0.59` | Materialize v0.59 | `releases-02.md` |
| `releases/v0.60` | Materialize v0.60 | `releases-02.md` |
| `releases/v0.61` | Materialize v0.61 | `releases-02.md` |
| `releases/v0.62` | Materialize v0.62 | `releases-02.md` |
| `releases/v0.63` | Materialize v0.63 | `releases-02.md` |
| `releases/v0.64` | Materialize v0.64 | `releases-02.md` |
| `releases/v0.65` | Materialize v0.65 | `releases-02.md` |
| `releases/v0.66` | Materialize v0.66 | `releases-02.md` |
| `releases/v0.67` | Materialize v0.67 | `releases-02.md` |
| `releases/v0.68` | Materialize v0.68 | `releases-02.md` |
| `releases/v0.69` | Materialize v0.69 | `releases-02.md` |
| `releases/v0.70` | Materialize v0.70 | `releases-02.md` |
| `releases/v0.71` | Materialize v0.71 | `releases-02.md` |
| `releases/v0.72` | Materialize v0.72 | `releases-02.md` |
| `releases/v0.73` | Materialize v0.73 | `releases-02.md` |
| `releases/v0.74` | Materialize v0.74 | `releases-02.md` |
| `releases/v0.75` | Materialize v0.75 | `releases-02.md` |
| `releases/v0.76` | Materialize v0.76 | `releases-02.md` |
| `releases/v0.77` | Materialize v0.77 | `releases-02.md` |
| `releases/v0.78` | Materialize v0.78 | `releases-02.md` |
| `releases/v0.79` | Materialize v0.79 | `releases-02.md` |
| `releases/v0.80` | Materialize v0.80 | `releases-02.md` |
| `releases/v0.81` | Materialize v0.81 | `releases-02.md` |
| `releases/v0.82` | Materialize v0.82 | `releases-02.md` |
| `releases/v0.83` | Materialize v0.83 | `releases-02.md` |
| `releases/v0.84` | Materialize v0.84 | `releases-02.md` |
| `releases/v0.85` | Materialize v0.85 | `releases-02.md` |
| `releases/v0.86` | Materialize v0.86 | `releases-02.md` |
| `releases/v0.87` | Materialize v0.87 | `releases-02.md` |
| `releases/v0.88` | Materialize v0.88 | `releases-02.md` |
| `releases/v0.89` | Materialize v0.89 | `releases-02.md` |
| `releases/v0.90` | Materialize v0.90 | `releases-02.md` |
| `releases/v0.91` | Materialize v0.91 | `releases-02.md` |
| `releases/v0.92` | Materialize v0.92 | `releases-02.md` |
| `releases/v0.93` | Materialize v0.93 | `releases-02.md` |
| `releases/v0.94` | Materialize v0.94 | `releases-02.md` |
| `releases/v0.95` | Materialize v0.95 | `releases-02.md` |
| `releases/v0.96` | Materialize v0.96 | `releases-02.md` |
| `releases/v0.97` | Materialize v0.97 | `releases-02.md` |
| `releases/v0.98` | Materialize v0.98 | `releases-02.md` |
| `releases/v0.99` | Materialize v0.99 | `releases-02.md` |
| `security` | Security | `security-01.md` |
| `security/appendix` | Appendix | `security-01.md` |
| `security/appendix/appendix-built-in-roles` | Appendix: Built-in roles | `security-01.md` |
| `security/appendix/appendix-command-privileges` | Appendix: Privileges by commands | `security-01.md` |
| `security/appendix/appendix-privileges` | Appendix: Privileges | `security-01.md` |
| `security/cloud` | Cloud | `security-01.md` |
| `security/cloud/access-control` | Access control (Role-based) | `security-01.md` |
| `security/cloud/access-control/manage-roles` | Manage database roles | `security-01.md` |
| `security/cloud/manage-network-policies` | Manage network policies | `security-01.md` |
| `security/cloud/users-service-accounts` | User and service accounts | `security-01.md` |
| `security/cloud/users-service-accounts/create-service-accounts` | Create service accounts | `security-01.md` |
| `security/cloud/users-service-accounts/invite-users` | Invite users | `security-01.md` |
| `security/cloud/users-service-accounts/sso` | Configure single sign-on (SSO) | `security-01.md` |
| `security/cloud/users-service-accounts/sync-idp-groups` | Sync identity provider groups to database roles | `security-01.md` |
| `security/fine-grained-access-control` | Fine-grained access control | `security-01.md` |
| `security/self-managed` | Self-managed | `security-01.md` |
| `security/self-managed/access-control` | Access control (Role-based) | `security-01.md` |
| `security/self-managed/access-control/manage-roles` | Manage database roles | `security-02.md` |
| `security/self-managed/authentication` | Authentication | `security-02.md` |
| `security/self-managed/sso` | Single sign-on (SSO) | `security-02.md` |
| `security/self-managed/sso-migration` | Migrate to SSO | `security-02.md` |
| `self-managed-deployments` | Self-Managed Deployments | `self-managed-deployments-01.md` |
| `self-managed-deployments/appendix` | Appendix | `self-managed-deployments-01.md` |
| `self-managed-deployments/appendix/appendix-cluster-sizes` | Cluster sizes | `self-managed-deployments-01.md` |
| `self-managed-deployments/appendix/upgrade-to-swap` | Prepare for swap and upgrade to v26.0 | `self-managed-deployments-01.md` |
| `self-managed-deployments/configuration-system-parameters` | Configuring System Parameters | `self-managed-deployments-01.md` |
| `self-managed-deployments/deployment-guidelines` | Deployment guidelines | `self-managed-deployments-01.md` |
| `self-managed-deployments/deployment-guidelines/aws-deployment-guidelines` | AWS deployment guidelines | `self-managed-deployments-01.md` |
| `self-managed-deployments/deployment-guidelines/azure-deployment-guidelines` | Azure deployment guidelines | `self-managed-deployments-01.md` |
| `self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines` | GCP deployment guidelines | `self-managed-deployments-01.md` |
| `self-managed-deployments/deployment-guidelines/gke-node-pool-upgrades` | GKE node pool upgrades | `self-managed-deployments-01.md` |
| `self-managed-deployments/deployment-guidelines/resize-node-pools` | Resize node pools | `self-managed-deployments-01.md` |
| `self-managed-deployments/faq` | FAQ | `self-managed-deployments-01.md` |
| `self-managed-deployments/installation` | Installation | `self-managed-deployments-01.md` |
| `self-managed-deployments/installation/install` | Install Self-Managed Materialize | `self-managed-deployments-01.md` |
| `self-managed-deployments/installation/install-on-aws` | Install on AWS | `self-managed-deployments-01.md` |
| `self-managed-deployments/installation/install-on-azure` | Install on Azure | `self-managed-deployments-01.md` |
| `self-managed-deployments/installation/install-on-gcp` | Install on GCP | `self-managed-deployments-01.md` |
| `self-managed-deployments/installation/install-on-local-kind` | Install locally on kind | `self-managed-deployments-01.md` |
| `self-managed-deployments/materialize-crd-field-descriptions` | Materialize CRD Field Descriptions | `self-managed-deployments-01.md` |
| `self-managed-deployments/materialize-crd-field-descriptions/v1` | v1 | `self-managed-deployments-02.md` |
| `self-managed-deployments/materialize-crd-field-descriptions/v1alpha1` | v1alpha1 | `self-managed-deployments-02.md` |
| `self-managed-deployments/operator-configuration` | Materialize Operator Configuration | `self-managed-deployments-02.md` |
| `self-managed-deployments/query-history` | Query History | `self-managed-deployments-02.md` |
| `self-managed-deployments/release-versions` | Self-managed release versions | `self-managed-deployments-02.md` |
| `self-managed-deployments/troubleshooting` | Troubleshooting | `self-managed-deployments-02.md` |
| `self-managed-deployments/upgrading` | Upgrading | `self-managed-deployments-02.md` |
| `self-managed-deployments/upgrading/adopting-the-v1-crd` | Adopting the v1 CRD | `self-managed-deployments-02.md` |
| `self-managed-deployments/upgrading/upgrade-on-aws` | Upgrade on AWS | `self-managed-deployments-02.md` |
| `self-managed-deployments/upgrading/upgrade-on-azure` | Upgrade on Azure | `self-managed-deployments-02.md` |
| `self-managed-deployments/upgrading/upgrade-on-gcp` | Upgrade on GCP | `self-managed-deployments-02.md` |
| `self-managed-deployments/upgrading/upgrade-on-kind` | Upgrade on kind | `self-managed-deployments-02.md` |
| `self-managed-deployments/upgrading/version-notes` | Upgrade notes | `self-managed-deployments-02.md` |
| `self-managed-deployments/usage` | Usage (Self-Managed) | `self-managed-deployments-02.md` |
| `serve-results` | Serve results | `serve-results-01.md` |
| `serve-results/adbc` | ADBC (Arrow Database Connectivity) | `serve-results-01.md` |
| `serve-results/bi-tools` | Use BI/data collaboration tools | `serve-results-01.md` |
| `serve-results/bi-tools/deepnote` | Deepnote | `serve-results-01.md` |
| `serve-results/bi-tools/excel` | Excel | `serve-results-01.md` |
| `serve-results/bi-tools/hex` | Hex | `serve-results-01.md` |
| `serve-results/bi-tools/looker` | Looker | `serve-results-01.md` |
| `serve-results/bi-tools/metabase` | Metabase | `serve-results-01.md` |
| `serve-results/bi-tools/power-bi` | Power BI | `serve-results-01.md` |
| `serve-results/bi-tools/tableau` | Tableau | `serve-results-01.md` |
| `serve-results/client-libraries` | Client libraries | `serve-results-01.md` |
| `serve-results/client-libraries/golang` | Golang cheatsheet | `serve-results-01.md` |
| `serve-results/client-libraries/java-jdbc` | Java cheatsheet | `serve-results-01.md` |
| `serve-results/client-libraries/node-js` | Node.js cheatsheet | `serve-results-01.md` |
| `serve-results/client-libraries/php` | PHP cheatsheet | `serve-results-01.md` |
| `serve-results/client-libraries/python` | Python cheatsheet | `serve-results-01.md` |
| `serve-results/client-libraries/ruby` | Ruby cheatsheet | `serve-results-01.md` |
| `serve-results/client-libraries/rust` | Rust cheatsheet | `serve-results-01.md` |
| `serve-results/connection-pooling` | Connection Pooling | `serve-results-01.md` |
| `serve-results/durable-subscriptions` | Durable subscriptions | `serve-results-01.md` |
| `serve-results/fdw` | Use foreign data wrapper (FDW) | `serve-results-01.md` |
| `serve-results/fdw-setup` | Foreign data wrapper (FDW) | `serve-results-01.md` |
| `serve-results/http-api` | Connect to Materialize via HTTP | `serve-results-01.md` |
| `serve-results/isolation-level` | Isolation levels | `serve-results-01.md` |
| `serve-results/query-results` | `SELECT` and `SUBSCRIBE` | `serve-results-01.md` |
| `serve-results/sql-clients` | SQL clients | `serve-results-01.md` |
| `serve-results/troubleshooting` | Troubleshooting | `serve-results-01.md` |
| `serve-results/websocket-api` | Connect to Materialize via WebSocket | `serve-results-01.md` |
| `sql` | SQL commands | `sql-01.md` |
| `sql/alter-cluster` | ALTER CLUSTER | `sql-01.md` |
| `sql/alter-cluster-replica` | ALTER CLUSTER REPLICA | `sql-01.md` |
| `sql/alter-connection` | ALTER CONNECTION | `sql-01.md` |
| `sql/alter-database` | ALTER DATABASE | `sql-01.md` |
| `sql/alter-default-privileges` | ALTER DEFAULT PRIVILEGES | `sql-01.md` |
| `sql/alter-index` | ALTER INDEX | `sql-01.md` |
| `sql/alter-materialized-view` | ALTER MATERIALIZED VIEW | `sql-01.md` |
| `sql/alter-network-policy` | ALTER NETWORK POLICY (Cloud) | `sql-01.md` |
| `sql/alter-role` | ALTER ROLE | `sql-01.md` |
| `sql/alter-schema` | ALTER SCHEMA | `sql-01.md` |
| `sql/alter-secret` | ALTER SECRET | `sql-01.md` |
| `sql/alter-sink` | ALTER SINK | `sql-01.md` |
| `sql/alter-source` | ALTER SOURCE | `sql-01.md` |
| `sql/alter-system-reset` | ALTER SYSTEM RESET | `sql-01.md` |
| `sql/alter-system-set` | ALTER SYSTEM SET | `sql-01.md` |
| `sql/alter-table` | ALTER TABLE | `sql-01.md` |
| `sql/alter-type` | ALTER TYPE | `sql-01.md` |
| `sql/alter-view` | ALTER VIEW | `sql-01.md` |
| `sql/begin` | BEGIN | `sql-01.md` |
| `sql/close` | CLOSE | `sql-01.md` |
| `sql/comment-on` | COMMENT ON | `sql-01.md` |
| `sql/commit` | COMMIT | `sql-01.md` |
| `sql/copy-from` | COPY FROM | `sql-01.md` |
| `sql/copy-to` | COPY TO | `sql-01.md` |
| `sql/create-cluster` | CREATE CLUSTER | `sql-01.md` |
| `sql/create-cluster-replica` | CREATE CLUSTER REPLICA | `sql-01.md` |
| `sql/create-connection` | CREATE CONNECTION | `sql-02.md` |
| `sql/create-database` | CREATE DATABASE | `sql-02.md` |
| `sql/create-index` | CREATE INDEX | `sql-02.md` |
| `sql/create-materialized-view` | CREATE MATERIALIZED VIEW | `sql-02.md` |
| `sql/create-network-policy` | CREATE NETWORK POLICY (Cloud) | `sql-02.md` |
| `sql/create-role` | CREATE ROLE | `sql-02.md` |
| `sql/create-schema` | CREATE SCHEMA | `sql-02.md` |
| `sql/create-secret` | CREATE SECRET | `sql-02.md` |
| `sql/create-sink` | CREATE SINK | `sql-02.md` |
| `sql/create-sink/iceberg` | CREATE SINK: Iceberg | `sql-02.md` |
| `sql/create-sink/kafka` | CREATE SINK: Kafka/Redpanda | `sql-02.md` |
| `sql/create-source` | CREATE SOURCE | `sql-02.md` |
| `sql/create-source/kafka` | CREATE SOURCE: Kafka/Redpanda (Legacy Syntax) | `sql-03.md` |
| `sql/create-source/kafka-v2` | CREATE SOURCE: Kafka/Redpanda (New Syntax) | `sql-03.md` |
| `sql/create-source/load-generator` | Appendix: Load generator | `sql-03.md` |
| `sql/create-source/mysql` | CREATE SOURCE: MySQL (Legacy syntax) | `sql-03.md` |
| `sql/create-source/mysql-v2` | CREATE SOURCE: MySQL (New Syntax) | `sql-03.md` |
| `sql/create-source/postgres` | CREATE SOURCE: PostgreSQL (Legacy Syntax) | `sql-03.md` |
| `sql/create-source/postgres-v2` | CREATE SOURCE: PostgreSQL (New Syntax) | `sql-04.md` |
| `sql/create-source/sql-server` | CREATE SOURCE: SQL Server (Legacy Syntax) | `sql-04.md` |
| `sql/create-source/sql-server-v2` | CREATE SOURCE: SQL Server | `sql-04.md` |
| `sql/create-source/webhook` | CREATE SOURCE: Webhook | `sql-04.md` |
| `sql/create-table` | CREATE TABLE | `sql-04.md` |
| `sql/create-table/kafka` | CREATE TABLE: Kafka source table | `sql-04.md` |
| `sql/create-table/mysql` | CREATE TABLE: MySQL source table | `sql-04.md` |
| `sql/create-table/postgres` | CREATE TABLE: PostgreSQL source table | `sql-04.md` |
| `sql/create-table/sql-server` | CREATE TABLE: SQL Server source table | `sql-04.md` |
| `sql/create-table/user-populated` | CREATE TABLE: Read-write table | `sql-04.md` |
| `sql/create-type` | CREATE TYPE | `sql-04.md` |
| `sql/create-view` | CREATE VIEW | `sql-04.md` |
| `sql/deallocate` | DEALLOCATE | `sql-04.md` |
| `sql/declare` | DECLARE | `sql-04.md` |
| `sql/delete` | DELETE | `sql-04.md` |
| `sql/discard` | DISCARD | `sql-04.md` |
| `sql/drop-cluster` | DROP CLUSTER | `sql-04.md` |
| `sql/drop-cluster-replica` | DROP CLUSTER REPLICA | `sql-04.md` |
| `sql/drop-connection` | DROP CONNECTION | `sql-04.md` |
| `sql/drop-database` | DROP DATABASE | `sql-04.md` |
| `sql/drop-index` | DROP INDEX | `sql-04.md` |
| `sql/drop-materialized-view` | DROP MATERIALIZED VIEW | `sql-04.md` |
| `sql/drop-network-policy` | DROP NETWORK POLICY (Cloud) | `sql-04.md` |
| `sql/drop-owned` | DROP OWNED | `sql-05.md` |
| `sql/drop-role` | DROP ROLE | `sql-05.md` |
| `sql/drop-schema` | DROP SCHEMA | `sql-05.md` |
| `sql/drop-secret` | DROP SECRET | `sql-05.md` |
| `sql/drop-sink` | DROP SINK | `sql-05.md` |
| `sql/drop-source` | DROP SOURCE | `sql-05.md` |
| `sql/drop-table` | DROP TABLE | `sql-05.md` |
| `sql/drop-type` | DROP TYPE | `sql-05.md` |
| `sql/drop-user` | DROP USER | `sql-05.md` |
| `sql/drop-view` | DROP VIEW | `sql-05.md` |
| `sql/execute` | EXECUTE | `sql-05.md` |
| `sql/execute-unit-test` | EXECUTE UNIT TEST | `sql-05.md` |
| `sql/explain-analyze` | EXPLAIN ANALYZE | `sql-05.md` |
| `sql/explain-filter-pushdown` | EXPLAIN FILTER PUSHDOWN | `sql-05.md` |
| `sql/explain-plan` | EXPLAIN PLAN | `sql-05.md` |
| `sql/explain-plan-operators` | Explain plan operators | `sql-05.md` |
| `sql/explain-schema` | EXPLAIN SCHEMA | `sql-05.md` |
| `sql/explain-timestamp` | EXPLAIN TIMESTAMP | `sql-05.md` |
| `sql/fetch` | FETCH | `sql-05.md` |
| `sql/functions` | SQL functions & operators | `sql-06.md` |
| `sql/functions/array_agg` | array_agg function | `sql-06.md` |
| `sql/functions/cast` | CAST function and operator | `sql-06.md` |
| `sql/functions/coalesce` | COALESCE function | `sql-06.md` |
| `sql/functions/csv_extract` | csv_extract function | `sql-06.md` |
| `sql/functions/date-bin` | date_bin function | `sql-06.md` |
| `sql/functions/date-part` | date_part function | `sql-06.md` |
| `sql/functions/date-trunc` | date_trunc function | `sql-06.md` |
| `sql/functions/datediff` | datediff function | `sql-06.md` |
| `sql/functions/encode` | encode and decode functions | `sql-06.md` |
| `sql/functions/extract` | EXTRACT function | `sql-06.md` |
| `sql/functions/filters` | Aggregate function filters | `sql-06.md` |
| `sql/functions/jsonb_agg` | jsonb_agg function | `sql-06.md` |
| `sql/functions/jsonb_object_agg` | jsonb_object_agg function | `sql-06.md` |
| `sql/functions/justify-days` | justify_days function | `sql-06.md` |
| `sql/functions/justify-hours` | justify_hours function | `sql-06.md` |
| `sql/functions/justify-interval` | justify_interval function | `sql-06.md` |
| `sql/functions/length` | LENGTH function | `sql-06.md` |
| `sql/functions/list_agg` | list_agg function | `sql-06.md` |
| `sql/functions/map_agg` | map_agg function | `sql-06.md` |
| `sql/functions/normalize` | normalize function | `sql-06.md` |
| `sql/functions/now_and_mz_now` | now and mz_now functions | `sql-06.md` |
| `sql/functions/pushdown` | Pushdown functions | `sql-06.md` |
| `sql/functions/string_agg` | string_agg function | `sql-06.md` |
| `sql/functions/substring` | SUBSTRING function | `sql-06.md` |
| `sql/functions/table-functions` | Table functions | `sql-06.md` |
| `sql/functions/timezone-and-at-time-zone` | TIMEZONE and AT TIME ZONE functions | `sql-06.md` |
| `sql/functions/to_char` | to_char function | `sql-06.md` |
| `sql/grant-privilege` | GRANT PRIVILEGE | `sql-06.md` |
| `sql/grant-role` | GRANT ROLE | `sql-06.md` |
| `sql/identifiers` | Identifiers | `sql-06.md` |
| `sql/insert` | INSERT | `sql-06.md` |
| `sql/namespaces` | Namespaces | `sql-06.md` |
| `sql/prepare` | PREPARE | `sql-06.md` |
| `sql/reassign-owned` | REASSIGN OWNED | `sql-06.md` |
| `sql/reset` | RESET | `sql-07.md` |
| `sql/revoke-privilege` | REVOKE PRIVILEGE | `sql-07.md` |
| `sql/revoke-role` | REVOKE ROLE | `sql-07.md` |
| `sql/rollback` | ROLLBACK | `sql-07.md` |
| `sql/select` | SELECT | `sql-07.md` |
| `sql/select/join` | JOIN | `sql-07.md` |
| `sql/select/recursive-ctes` | Recursive CTEs | `sql-07.md` |
| `sql/set` | SET | `sql-07.md` |
| `sql/show` | SHOW | `sql-07.md` |
| `sql/show-cluster-replicas` | SHOW CLUSTER REPLICAS | `sql-07.md` |
| `sql/show-clusters` | SHOW CLUSTERS | `sql-07.md` |
| `sql/show-columns` | SHOW COLUMNS | `sql-07.md` |
| `sql/show-connections` | SHOW CONNECTIONS | `sql-07.md` |
| `sql/show-create-cluster` | SHOW CREATE CLUSTER | `sql-07.md` |
| `sql/show-create-connection` | SHOW CREATE CONNECTION | `sql-07.md` |
| `sql/show-create-index` | SHOW CREATE INDEX | `sql-07.md` |
| `sql/show-create-materialized-view` | SHOW CREATE MATERIALIZED VIEW | `sql-07.md` |
| `sql/show-create-sink` | SHOW CREATE SINK | `sql-07.md` |
| `sql/show-create-source` | SHOW CREATE SOURCE | `sql-07.md` |
| `sql/show-create-table` | SHOW CREATE TABLE | `sql-07.md` |
| `sql/show-create-type` | SHOW CREATE TYPE | `sql-07.md` |
| `sql/show-create-view` | SHOW CREATE VIEW | `sql-07.md` |
| `sql/show-databases` | SHOW DATABASES | `sql-07.md` |
| `sql/show-default-privileges` | SHOW DEFAULT PRIVILEGES | `sql-07.md` |
| `sql/show-indexes` | SHOW INDEXES | `sql-07.md` |
| `sql/show-materialized-views` | SHOW MATERIALIZED VIEWS | `sql-07.md` |
| `sql/show-network-policies` | SHOW NETWORK POLICIES (Cloud) | `sql-07.md` |
| `sql/show-objects` | SHOW OBJECTS | `sql-07.md` |
| `sql/show-privileges` | SHOW PRIVILEGES | `sql-07.md` |
| `sql/show-role-membership` | SHOW ROLE MEMBERSHIP | `sql-07.md` |
| `sql/show-roles` | SHOW ROLES | `sql-07.md` |
| `sql/show-schemas` | SHOW SCHEMAS | `sql-07.md` |
| `sql/show-secrets` | SHOW SECRETS | `sql-07.md` |
| `sql/show-sinks` | SHOW SINKS | `sql-07.md` |
| `sql/show-sources` | SHOW SOURCES | `sql-07.md` |
| `sql/show-subsources` | SHOW SUBSOURCES | `sql-07.md` |
| `sql/show-tables` | SHOW TABLES | `sql-07.md` |
| `sql/show-types` | SHOW TYPES | `sql-07.md` |
| `sql/show-views` | SHOW VIEWS | `sql-07.md` |
| `sql/subscribe` | SUBSCRIBE | `sql-07.md` |
| `sql/system-catalog` | System catalog | `sql-07.md` |
| `sql/system-catalog/information_schema` | information_schema | `sql-07.md` |
| `sql/system-catalog/mz_catalog` | mz_catalog | `sql-08.md` |
| `sql/system-catalog/mz_internal` | mz_internal | `sql-08.md` |
| `sql/system-catalog/mz_introspection` | mz_introspection | `sql-09.md` |
| `sql/system-catalog/pg_catalog` | pg_catalog | `sql-09.md` |
| `sql/table` | TABLE | `sql-09.md` |
| `sql/types` | SQL data types | `sql-09.md` |
| `sql/types/array` | Array types | `sql-09.md` |
| `sql/types/boolean` | boolean type | `sql-09.md` |
| `sql/types/bytea` | bytea type | `sql-09.md` |
| `sql/types/date` | date type | `sql-09.md` |
| `sql/types/float` | Floating-point types | `sql-09.md` |
| `sql/types/integer` | Integer types | `sql-09.md` |
| `sql/types/interval` | interval type | `sql-09.md` |
| `sql/types/jsonb` | jsonb type | `sql-09.md` |
| `sql/types/list` | List types | `sql-09.md` |
| `sql/types/map` | map type | `sql-09.md` |
| `sql/types/mz_aclitem` | mz_aclitem type | `sql-09.md` |
| `sql/types/mz_timestamp` | mz_timestamp type | `sql-09.md` |
| `sql/types/numeric` | numeric type | `sql-09.md` |
| `sql/types/oid` | oid type | `sql-09.md` |
| `sql/types/record` | record type | `sql-09.md` |
| `sql/types/text` | text type | `sql-09.md` |
| `sql/types/time` | time type | `sql-09.md` |
| `sql/types/timestamp` | Timestamp types | `sql-09.md` |
| `sql/types/uint` | Unsigned Integer types | `sql-09.md` |
| `sql/types/uuid` | uuid type | `sql-09.md` |
| `sql/update` | UPDATE | `sql-09.md` |
| `sql/validate-connection` | VALIDATE CONNECTION | `sql-09.md` |
| `sql/values` | VALUES | `sql-09.md` |
| `support` | Support | `support-01.md` |
| `transform-data` | Overview | `transform-data-01.md` |
| `transform-data/dataflow-troubleshooting` | Dataflow troubleshooting | `transform-data-01.md` |
| `transform-data/dictionary-compression` | Dictionary compression | `transform-data-01.md` |
| `transform-data/faq` | FAQ: Indexes | `transform-data-01.md` |
| `transform-data/freshness-troubleshooting` | Freshness troubleshooting | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql` | Idiomatic Materialize SQL | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/any` | `ANY()` equi-join condition | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/appendix` | Appendix | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/appendix/example-orders` | Example data: items and orders | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/appendix/idiomatic-sql-chart` | Idiomatic Materialize SQL chart | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/appendix/window-function-to-materialize` | Window function to idiomatic Materialize | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/first-value` | First value in group | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/lag` | Lag over | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/last-value` | Last value in group | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/lead` | Lead over | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/mz_now` | mz_now() expressions | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/not-in` | `NOT IN` subquery | `transform-data-01.md` |
| `transform-data/idiomatic-materialize-sql/top-k` | Top-K in group | `transform-data-02.md` |
| `transform-data/monitor-freshness` | How to monitor freshness in Materialize | `transform-data-02.md` |
| `transform-data/optimization` | Optimization | `transform-data-02.md` |
| `transform-data/patterns` | Patterns | `transform-data-02.md` |
| `transform-data/patterns/ontology` | Use an ontology table | `transform-data-02.md` |
| `transform-data/patterns/partition-by` | Partitioning and filter pushdown | `transform-data-02.md` |
| `transform-data/patterns/percentiles` | Percentile calculation | `transform-data-02.md` |
| `transform-data/patterns/refresh-strategies` | Refresh strategies and scheduled clusters | `transform-data-02.md` |
| `transform-data/patterns/rules-engine` | Rules execution engine | `transform-data-02.md` |
| `transform-data/patterns/temporal-filters` | Temporal filters (time windows) | `transform-data-02.md` |
| `transform-data/updating-materialized-views` | Updating materialized views | `transform-data-02.md` |
| `transform-data/updating-materialized-views/replace-materialized-view` | Replace Materialized Views | `transform-data-02.md` |
