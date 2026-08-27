# Materialize Agent Skills

Agent skills to help developers build with [Materialize](https://materialize.com/), a streaming database for real-time analytics. Agent skills are folders of instructions, scripts, and resources that AI agents like Claude Code, Cursor, GitHub Copilot, and others can discover and use to work more accurately and efficiently.

The skills in this repo follow the [Agent Skills Open Standard](https://agentskills.io/).

## Installation

```bash
npx skills add MaterializeInc/agent-skills
```

Once installed, skills activate automatically when your prompt matches their use case.

## Available Skills

<details>
<summary><strong>materialize-docs</strong></summary>

Materialize documentation for SQL syntax, data ingestion, concepts, and best practices.

**Use when:**

- Writing or debugging Materialize SQL queries
- Setting up sources (Kafka, PostgreSQL, MySQL, webhooks, etc.)
- Creating materialized views, indexes, or sinks
- Configuring clusters or deployment settings
- Working with data ingestion or transformation patterns

**Categories covered:**

- SQL Commands (120+ command references)
- Core Concepts (clusters, sources, sinks, views, indexes)
- Data Ingestion (Kafka, PostgreSQL, MySQL, MongoDB, SQL Server, webhooks)
- Data Transformation (patterns, optimization, idiomatic SQL)
- Serving Results (sinks, BI tools, FDW)
- Integrations (CLI, client libraries, HTTP/WebSocket APIs)
- Security (RBAC, network policies, SSO)
- Self-Managed Deployments (AWS, Azure, GCP, Kubernetes)
- Management (monitoring, dbt, Terraform, disaster recovery)

**Synced with the [online Materialize documentation](https://materialize.com/docs/).** Either one can be used to identify the Materialize version that introduced or updated a particular feature.

</details>

<details>
<summary><strong>materialize-terraform-provider</strong></summary>

Using the Materialize Terraform provider to manage Materialize resources declaratively, for both Cloud and self-managed deployments.

**Use when:**

- Writing Terraform for Materialize resources (clusters, sources, sinks, connections, views, grants)
- Configuring the Materialize provider for Cloud or self-managed
- Importing existing Materialize objects into Terraform state
- Setting up RBAC, secrets, or network policies via Terraform
- Troubleshooting Terraform plan/apply issues with `materialize_*` resources

**Covers:** provider configuration, a resource category map, cross-resource patterns, import workflows, and gotchas. Per-resource argument reference intentionally stays in the [auto-generated provider docs](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs), which the skill teaches agents to navigate.

</details>

<details>
<summary><strong>materialize-terraform-self-managed</strong></summary>

Terraform modules for deploying self-managed Materialize on AWS (EKS), Azure (AKS), and GCP (GKE).

**Use when:**

- Deploying self-managed Materialize with Terraform on any cloud
- Customizing the networking, Kubernetes, database, or storage modules
- Configuring the Materialize operator or instance (CRD versions, rollout strategies)
- Pulling the modules into an existing Terraform project with pinned Git sources
- Upgrading Materialize instances or troubleshooting a deployment

**Covers:** module layout and variables for all three clouds, backend URL formats, storage authentication support, instance sizing, post-deployment setup, upgrades, and common gotchas from the [materialize-terraform-self-managed](https://github.com/MaterializeInc/materialize-terraform-self-managed) repository.

</details>

<details>
<summary><strong>materialize-dbt</strong></summary>

Using the dbt-materialize adapter to manage Materialize streaming pipelines with dbt.

**Use when:**

- Writing dbt models for Materialize, or migrating an existing dbt project to it
- Configuring dbt profiles for Materialize
- Running blue/green or zero-downtime deployments with dbt
- Creating sources or sinks in dbt
- Troubleshooting dbt-materialize issues

**Covers:** every materialization (`source`, `source_table`, `view`, `materialized_view`, `sink`, `table`, `seed`), profile configuration, indexes, strict mode, the blue/green macros (`deploy_init`, `deploy_await`, `deploy_promote`, `deploy_cleanup`), cluster management, slim deployments, model contracts, and gotchas.

</details>

<details>
<summary><strong>mz-deploy</strong></summary>

Using the [`mz-deploy`](https://materialize.com/) CLI to manage a declarative SQL project and deploy changes to Materialize safely.

**Use when:**

- Working in an mz-deploy project (any directory containing `project.toml`)
- Deploying SQL changes through the stage → wait → promote lifecycle
- Managing infrastructure declaratively with `mz-deploy apply`
- Writing `EXECUTE UNIT TEST` tests for views
- Rolling back a deployment or resolving a deployment conflict

**Covers:** project layout, the `compile → test → apply → stage → wait → promote` workflow, hash-based change detection, atomic `ALTER … SWAP` promotion, conflict detection, stable API schemas (`SET api = stable`) and replacement materialized views, offline type checking with `types.lock`, per-profile suffixes/variables/file overrides, and a full reference for the `EXECUTE UNIT TEST` syntax. Per-command flags intentionally stay in `mz-deploy help <command>`, which the skill teaches agents to consult.

</details>

<details>
<summary><strong>mz-ontology-design</strong></summary>

Designing the semantic layer of a Materialize SQL code base as a canonical ontology: a shared `raw` database, a shared `core` database, and one database per use case.

**Use when:**

- Deciding how to organize databases and schemas across a Materialize code base
- Deciding whether a new relation belongs in the shared ontology or at a consumer edge
- Defining semantic objects (entities, events, measurements, relationship objects) with a documented grain
- Resolving cross-source identity, or declaring temporal semantics for a public object
- Building or validating the `core.public.relationships` reference-edge registry
- Reviewing an existing code base for leaked private schemas, duplicated concepts, or undocumented public objects

**Covers:** the `raw` -> `core.<source_system>` -> `core.internal` -> `core.public` -> `<use_case>` dependency direction and how to enforce it, the admission test for a public semantic object, identity and time rules, normalization and denormalization, reference edges versus relationship objects, and the `comment on` documentation contract plus the tests and CI checks that keep the boundaries honest. Includes the relationship registry SQL as a reference.

</details>

<details>
<summary><strong>materialize-environment-analysis</strong></summary>

Analyze a Materialize environment via the MCP Developer endpoint, and/or configure an MCP client (Claude Code, Cursor, VS Code, Zed, Continue, Windsurf, Claude Desktop) to connect to the materialize-developer server.

**Use when:**

- Checking environment health
- Investigating performance issues
- Troubleshooting stale materialized views
- Diagnosing memory pressure
- Auditing resource utilization
- Getting optimization recommendations
- Configuring an MCP client to connect to materialize-developer (Emulator, Cloud, or self-managed)
- Controlling which user or role the connection uses
- Switching between identities

</details>

<details>
<summary><strong>materialize-debug-freshness</strong></summary>

Diagnosing why a Materialize object is behind wall-clock time, from the lag ranking down to the operator and the SQL responsible.

**Use when:**

- An object shows high lag in `mz_wallclock_global_lag`, or a freshness alert fires
- A materialized view, index, or sink keeps serving old data
- A dataflow cannot keep up with its input
- You need to know whether the delay is ingestion or compute, and which object owns it

**Covers:** the lag ranking read as a distribution, the status sweep that catches a stalled source whose frontier still looks current, lag history for spike against plateau, hop-by-hop attribution through `mz_materialization_lag`, hydration and replica selection before any `EXPLAIN ANALYZE`, ranking dataflows on a shared replica, per-operator cost and worker skew, and mapping an operator back through inlined views to the clause that produced it. Diagnosis only — remedies are a separate request.

</details>

## Claude Code Plugins

This repo also doubles as a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces), for capabilities that go beyond what a portable skill can express — such as registering a language server.

```
/plugin marketplace add MaterializeInc/agent-skills
```

<details>
<summary><strong>mz-sql-lsp</strong></summary>

Registers the `mz-deploy` language server for `.sql` files, so Claude's LSP tool can resolve go-to-definition, hover, and document/workspace symbols across an mz-deploy project instead of grepping. Bundles a skill that teaches Claude when to use it.

```
/plugin install mz-sql-lsp@materialize
```

**Requires** `mz-deploy` on `PATH`, and one setting on enable: the directory containing `project.toml`, relative to your repository root.

See [plugins/mz-sql-lsp](plugins/mz-sql-lsp/README.md) for configuration and troubleshooting.

</details>

## Usage

Skills are automatically available once installed. The agent will use them when relevant tasks are detected.

**Examples:**

```
How do I create a Kafka source in Materialize?
```

```
Help me set up a materialized view that joins two sources
```

```
What's the syntax for CREATE SINK?
```
Skills can also be explicitly invoked in user prompts:

```
❯ /materialize-docs what sources are supported?
```

## Compatibility

This skill follows the [Agent Skills Open Standard](https://agentskills.io/) and is compatible with 30+ AI agents, including:

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Cursor](https://cursor.sh/)
- [GitHub Copilot](https://github.com/features/copilot)
- [Cline](https://cline.bot/)
- [Windsurf](https://codeium.com/windsurf)

## Skill Structure

Each skill follows the Agent Skills Open Standard:

```
skills/
  {skill-name}/
    SKILL.md              # Required: skill manifest with frontmatter
    README.md             # Optional: user-facing documentation
    references/           # Optional: curated reference material
    {topic}/              # Topic directories containing documentation
      index.md
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

See [LICENSE](LICENSE).

## Changelog

- 2026-08-27: Rename mcp-developer-analysis to materialize-environment-analysis
- 2026-08-24: Add mz-ontology-design skill
- 2026-08-18: Add materialize-debug-freshness skill
- 2026-08-14: Add mz-deploy skill
- 2026-07-29: Add mz-sql-lsp Claude Code plugin
- 2026-07-09: Add materialize-terraform-self-managed skill
- 2026-07-09: Add materialize-terraform-provider skill
- 2026-05-08: Add MCP client setup playbook to mcp-developer-analysis
- 2026-05-05: Rename mz-developer-analysis to mcp-developer-analysis
- 2026-04-28: Add mcp-developer-analysis skill
- 2026-02-09: Add materialize-docs skill
