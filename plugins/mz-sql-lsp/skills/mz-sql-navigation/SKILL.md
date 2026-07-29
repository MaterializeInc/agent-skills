---
name: mz-sql-navigation
description: Use when reading or editing .sql files in an mz-deploy project (a directory with project.toml) — resolve object references, columns, and types with the LSP tool instead of grepping. Covers go-to-definition, hover, and document/workspace symbols for Materialize SQL.
---

# Navigating Materialize SQL

The `mz-deploy` language server answers questions about an mz-deploy project's object
graph. Use the LSP tool for these instead of text search — grep finds strings that look
like an object name, the language server finds the object.

## What to use it for

- **Go to definition** — resolve where a referenced view, table, source, or index is
  defined, including across schemas.
- **Hover** — inspect an object's columns and their types without opening its definition.
- **Document symbols** — list the objects a single `.sql` file defines.
- **Workspace symbols** — locate an object by name when you don't know its file.

Before changing an object, use these to find what depends on it. In Materialize a view's
definition constrains everything downstream of it, so an edit that type-checks in
isolation can still break dependents.

## Diagnostics

Parse errors surface automatically after each edit. Treat them as authoritative for
syntax; they come from the same parser `mz-deploy` uses to build the project.

## Requirements

`mz-deploy` must be on `PATH` (`which mz-deploy`). If every navigation request comes back
empty while the server looks healthy, the plugin's **mz-deploy project directory**
setting is pointing somewhere other than the directory holding `project.toml`. The
server takes that directory as its project root, and a project nested in a subdirectory
needs the setting to name that subdirectory. Report this rather than falling back to
grep — a stale setting is worth fixing once.
