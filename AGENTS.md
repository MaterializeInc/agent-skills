# AGENTS.md

Guidance for AI coding agents (Claude Code, Cursor, Copilot, etc.) working with this repository.

## Repository Overview

A collection of skills for AI agents working with [Materialize](https://materialize.com/), a streaming database for real-time analytics. Skills are packaged instructions and documentation that extend agent capabilities when helping users with Materialize.

## Repository Structure

```
skills/
  {skill-name}/
    SKILL.md              # Required: skill manifest (Agent Skills spec)
    README.md             # Optional: user-facing documentation
    references/           # Optional: curated reference material
      README.md
    {topic}/              # Topic directories containing documentation
      index.md
```

### Current Skills

| Skill | Description |
|-------|-------------|
| `materialize-docs` | Materialize documentation for SQL syntax, data ingestion, concepts, and best practices |

## Working with Skills

### Reading Documentation

When answering questions about Materialize, navigate the `skills/materialize-docs/` directory:

- **SQL syntax and commands**: `sql/` (120+ command references)
- **Core concepts**: `concepts/` (clusters, sources, sinks, views, indexes)
- **Data ingestion**: `ingest-data/` (Kafka, PostgreSQL, MySQL, webhooks, etc.)
- **Data transformation**: `transform-data/` (patterns, optimization, idiomatic SQL)
- **Serving results**: `serve-results/` (sinks, BI tools, FDW)
- **Integrations**: `integrations/` (CLI, client libraries, HTTP/WebSocket APIs)
- **Security**: `security/` (RBAC, network policies, SSO)
- **Deployment**: `self-managed-deployments/` (AWS, Azure, GCP, Kubernetes)
- **Management**: `manage/` (monitoring, dbt, Terraform, disaster recovery)
- **Console**: `console/` (Materialize web UI)

Each topic directory contains an `index.md` with the full documentation for that topic.

### SKILL.md Anatomy

The `SKILL.md` file in each skill directory contains a quick-reference map of all available documentation. Start there to locate relevant files before reading individual docs.

## Creating a New Skill

Skills follow the [Agent Skills Open Standard](https://agentskills.io/).

### Directory Structure

```
skills/
  {skill-name}/
    SKILL.md              # Required: skill definition with frontmatter
    README.md             # Optional: human-readable overview
    references/           # Optional: curated authoritative sources
```

### Naming Conventions

- **Skill directory**: `kebab-case` (e.g., `materialize-docs`, `materialize-recipes`)
- **SKILL.md**: Always uppercase, always this exact filename
- **Topic directories**: `kebab-case` matching the documentation topic

### SKILL.md Format

```yaml
---
name: skill-name
description: What this skill does and when to use it. Include trigger keywords.
---
```

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1-64 chars. Lowercase alphanumeric and hyphens only. Must match directory name. |
| `description` | Yes | 1-1024 chars. Describe what the skill does AND when to use it. |
| `license` | No | License name or reference to bundled license file. |
| `metadata` | No | Arbitrary key-value pairs (e.g., `author`, `version`). |

#### Name Rules

- Lowercase letters, numbers, and hyphens only (`a-z`, `0-9`, `-`)
- Must not start or end with `-`
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name exactly

#### Description Best Practices

The description is the **primary trigger mechanism**. Agents use it to decide when to activate the skill.

```yaml
# Good - specific and trigger-rich
description: >
  Materialize documentation for SQL syntax, data ingestion, concepts,
  and best practices. Use when users ask about Materialize queries,
  sources, sinks, views, or clusters.

# Bad - too vague
description: Materialize help.
```

### Body Content

The Markdown body after the frontmatter contains instructions and a navigation map. Guidelines:

- Keep under 500 lines; move detailed content to separate files
- Use progressive disclosure: SKILL.md summarizes, reference files have full details
- Prefer concise examples over verbose explanations

### Progressive Disclosure

Skills load in three stages:

1. **Metadata** (~100 tokens): `name` and `description` loaded at startup for all skills
2. **Instructions** (<5000 tokens recommended): Full `SKILL.md` body loaded when skill activates
3. **Resources** (as needed): Individual documentation files loaded on demand

## Adding Documentation

When adding new documentation to an existing skill:

1. Create the appropriate directory under the skill (e.g., `skills/materialize-docs/{section}/{topic}/`)
2. Add an `index.md` file with the documentation content
3. Update the skill's `SKILL.md` to reference the new documentation in the appropriate section

## End-User Installation

### Using the Skills CLI (recommended)

Install skills from this repository using the [Skills CLI](https://github.com/vercel-labs/skills):

```bash
# Install all skills from this repo
npx skills add MaterializeInc/agent-skills

# Install a specific skill
npx skills add MaterializeInc/agent-skills@materialize-docs
```

The CLI auto-detects installed agents (Claude Code, Cursor, Cline, etc.) and
installs the skill to each one.

### Manual installation

**Claude Code:**
```bash
cp -r skills/{skill-name} ~/.claude/skills/
```

**Claude.ai:**
Add `SKILL.md` to project knowledge or paste its contents into the conversation.

## Verifying Installation

After installing, confirm the skill is available:

```bash
# Check the skill was copied/symlinked correctly
ls ~/.claude/skills/materialize-docs/SKILL.md

# For a local (development) install from a checkout of this repo
npx skills add ./
```
