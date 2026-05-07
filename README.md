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

**Source:** Synced with the [online Materialize documentation](https://materialize.com/docs/). Either source can be used to identify the Materialize version that introduced or updated a particular feature.

</details>

<details>
<summary><strong>mcp-developer-analysis</strong></summary>

Analyze a Materialize environment for health, performance, and optimization opportunities using the MCP Developer endpoint.

**Use when:**

- Checking environment health
- Investigating performance issues
- Troubleshooting stale materialized views
- Diagnosing memory pressure
- Auditing resource utilization
- Getting optimization recommendations

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

- 2026-05-05: Rename mz-developer-analysis to mcp-developer-analysis
- 2026-04-28: Add mcp-developer-analysis skill
- 2026-02-09: Add materialize-docs skill
