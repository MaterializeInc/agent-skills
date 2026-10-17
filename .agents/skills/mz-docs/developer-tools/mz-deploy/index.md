# Use mz-deploy to manage Materialize

Deploy and manage Materialize objects with mz-deploy, a SQL-native CLI for zero-downtime deployments.

`mz-deploy` is a CLI that manages your Materialize deployment from plain SQL
files in a git repository. It catches errors before they reach production, lets
you test view logic locally, and deploys changes without downtime.

## Installation

On macOS and Linux, we recommend installing `mz-deploy` with
[Homebrew](https://brew.sh/):

```shell
brew install materializeinc/materialize/mz-deploy
```

For direct downloads and other installation options, see
[Get started](/developer-tools/mz-deploy/get-started/#prerequisites-and-installation).

## Why mz-deploy

### Write plain SQL, deploy safely

Everything lives in `.sql` files — one object per file, organized by database
and schema. `mz-deploy` tracks dependencies between objects, diffs your project
against the live environment, and deploys only what changed. Durable objects
like secrets, connections, sources, and tables are converged in place (like
Terraform). Views, materialized views, indexes, and sinks go through a staged
deployment so changes can be validated before going live.

### Catch errors before deploying

`mz-deploy compile` type-checks every SQL statement against your dependency
schemas — locally, with no database connection required. Inline unit tests let
you mock dependencies and verify view logic with deterministic inputs before
anything touches a real environment. Changes that break types or dependencies
fail fast on your laptop or in CI, not in production.

### Ship without downtime

When you deploy, `mz-deploy` creates your changes in isolated staging schemas
alongside production. Once all materialized views finish computing their initial
results, a single atomic swap cuts traffic over to the new version. Running
queries are never interrupted, and if something goes wrong, the staging
deployment can be cleaned up without affecting production.

## When to use it

| Tool | Best for | Manages infrastructure | Zero-downtime deployments |
|------|----------|----------------------|--------------------------|
| **Plain SQL / psql scripts** | Manual execution. No dependency tracking, no diff, no rollback. Where most teams start. | No | No |
| **mz-deploy** | SQL-native, git-based workflow with offline type-checking, unit tests, and staged deployments. | Yes | Yes |
| **[dbt](/developer-tools/dbt/)** | Teams already invested in dbt. Manages views and materialized views. | No (clusters, connections, secrets are out of scope) | Yes (via `dbt-materialize` adapter macros) |
| **[Terraform](/developer-tools/terraform/)** | Teams managing Materialize alongside other cloud infrastructure. | Yes | No |

## Available guides

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    To get started
  </div>
  <a href="/developer-tools/mz-deploy/get-started/" >Get started with mz-deploy</a>
</div>

<div class="linkbox ">
  <div class="title">
    Develop
  </div>
  <ul>
<li><a href="/developer-tools/mz-deploy/project-structure/" >Project structure</a></li>
<li><a href="/developer-tools/mz-deploy/infrastructure/" >Infrastructure</a></li>
<li><a href="/developer-tools/mz-deploy/local-development/" >Local development</a></li>
<li><a href="/developer-tools/mz-deploy/editor-setup/" >Editor setup</a></li>
<li><a href="/developer-tools/mz-deploy/agent-setup/" >AI agent setup</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Deploy
  </div>
  <ul>
<li><a href="/developer-tools/mz-deploy/deployments/" >Deployments</a></li>
<li><a href="/developer-tools/mz-deploy/stable-apis/" >Stable APIs</a></li>
<li><a href="/developer-tools/mz-deploy/profiles/" >Profiles</a></li>
</ul>

</div>

</div>

## Pages in this section

- [AI agent setup](/developer-tools/mz-deploy/agent-setup/index.md): Configure AI coding agents like Claude Code and Codex to work with mz-deploy projects.
- [Deployments](/developer-tools/mz-deploy/deployments/index.md): Stage, test, and promote zero-downtime blue/green deployments.
- [Editor setup](/developer-tools/mz-deploy/editor-setup/index.md): Configure VS Code, Neovim, or Helix with the mz-deploy language server.
- [Get started with mz-deploy](/developer-tools/mz-deploy/get-started/index.md): Set up mz-deploy and deploy your first project to Materialize.
- [Infrastructure](/developer-tools/mz-deploy/infrastructure/index.md): Manage clusters, roles, secrets, connections, sources, and tables with mz-deploy apply.
- [Local development](/developer-tools/mz-deploy/local-development/index.md): Type-check, test, and inspect query plans locally before deploying.
- [Profiles](/developer-tools/mz-deploy/profiles/index.md): Configure multiple environments with profiles, variables, and file overrides.
- [Project structure](/developer-tools/mz-deploy/project-structure/index.md): How mz-deploy projects are organized: directories, model files, and configuration.
- [Stable APIs](/developer-tools/mz-deploy/stable-apis/index.md): Build cross-team data products with stable API schemas that never break downstream consumers.
