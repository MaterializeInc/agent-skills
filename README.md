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


<details>
<summary><strong>mcp-developer-analysis</strong></summary>

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

- 2026-07-09: Add materialize-terraform-self-managed skill
- 2026-07-09: Add materialize-terraform-provider skill
- 2026-05-08: Add MCP client setup playbook to mcp-developer-analysis
- 2026-05-05: Rename mz-developer-analysis to mcp-developer-analysis
- 2026-04-28: Add mcp-developer-analysis skill
- 2026-02-09: Add materialize-docs skill
