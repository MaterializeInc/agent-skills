# mz-sql-lsp

Registers the `mz-deploy` language server for `.sql` files so Claude Code's LSP tool can
resolve go-to-definition, hover, and document/workspace symbols across an
[mz-deploy](https://materialize.com/docs/) project.

Ships with the `mz-sql-navigation` skill, which tells Claude to reach for the LSP tool
rather than grepping when it needs to resolve an object reference, inspect a view's
columns, or find dependents before an edit.

## Requirements

`mz-deploy` must be on `PATH`:

```bash
which mz-deploy
```

## Installation

```
/plugin marketplace add MaterializeInc/agent-skills
/plugin install mz-sql-lsp@materialize
```

## Configuration

The plugin requires one setting, **mz-deploy project directory** — the directory
containing `project.toml`, relative to your repository root. Claude Code prompts for it
when you enable the plugin.

| Layout | Setting |
|--------|---------|
| `project.toml` at the repository root | `.` |
| Project nested in a subdirectory, e.g. `mz/project.toml` | `mz` |

This setting is load-bearing and has no working fallback. The language server takes the
directory as its project root, so a value pointing at the wrong place makes every
navigation request return "No definition found" while the server still appears healthy.

If you dismiss the prompt without entering a value, the LSP server does not load and
Claude Code logs:

```
Failed to load LSP servers for plugin mz-sql-lsp: Error: Plugin option
"project_dir" isn't set. Open /plugin manage to configure it
```

Run `/plugin`, open the plugin's detail view, and set the value to fix it or change it
later.

## Supported extensions

`.sql`

If another enabled LSP server also claims `.sql`, the first one registered wins and the
other never starts. The `/plugin` interface names the plugin whose server is active.

## Troubleshooting

| Symptom | Cause |
|---------|-------|
| `Plugin option "project_dir" isn't set` | Set **mz-deploy project directory** via `/plugin` |
| Every request returns "No definition found" | The setting points somewhere other than the directory holding `project.toml` |
| `Executable not found in $PATH` | Install `mz-deploy`; confirm with `which mz-deploy` |
| `ENOENT ... posix_spawn 'mz-deploy'` | The resolved project directory does not exist, so the server's working directory is invalid. Despite naming the binary, this is a path problem, not a `PATH` problem |
| Server never starts | Run `claude --debug` — it reports why a server was skipped |
