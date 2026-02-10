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

Comprehensive Materialize documentation covering SQL syntax, data ingestion, concepts, and best practices. Contains 400+ reference files across 18 categories.

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
