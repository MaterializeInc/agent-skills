# materialize-debug-freshness

This skill helps you find out why a Materialize object is behind the current time. You can use it through the [MCP developer endpoint](https://materialize.com/docs/integrations/mcp-server/mcp-developer/).

## What it does

You give it a sign of lag, such as high `mz_wallclock_global_lag`, a stale view, or a dashboard with old data. It finds the exact object and the reason for the lag:

- It finds the object that causes the lag, not just the objects that show it.
- It tells you if the problem is with data coming in (ingestion) or with processing (compute).
- For compute problems, it checks the replica before the object, because dataflows share CPU and memory and a lagging object may be starved by a different one.
- It links slow operators back to their SQL code using its own cost SQL and `EXPLAIN PHYSICAL PLAN WITH (node identifiers)`.

The deliverable is the diagnosis. Remedies are a separate request.

## Layout

```
materialize-debug-freshness/
├── SKILL.md                          # the workflow
└── references/
    ├── attribution.md                # catalog queries for steps 1-5
    └── dataflow-analysis.md          # EXPLAIN reference for steps 6-8
```

## Setup

Connect an MCP client to the Materialize developer endpoint. This endpoint has the `query_system_catalog` and `query` tools. Check the [MCP Server for Developers](https://materialize.com/docs/integrations/mcp-server/mcp-developer/) documentation.

## Scope

Freshness only: an object behind wall-clock time. Diagnosis, not remediation.

Memory-only problems, cost and credit questions, index advice, and general
environment health are outside it. So is ad-hoc query latency, which has no row
in `mz_wallclock_global_lag`.
