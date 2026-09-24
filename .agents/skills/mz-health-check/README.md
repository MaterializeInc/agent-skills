# MCP Developer Analysis

A skill for analyzing Materialize environments via the built-in
[MCP developer endpoint](https://materialize.com/docs/integrations/mcp-server/mcp-developer/)
(`/api/mcp/developer`).

## What it does

Connect an MCP-compatible AI agent (Claude Code, Claude Desktop, Cursor) to your
Materialize environment and ask natural language questions like:

- "Why is my materialized view stale?"
- "Why is my cluster running out of memory?"
- "What can I optimize to save costs?"
- "What's the health of my environment?"

The skill provides the AI agent with:

- **Verified diagnostic queries** against the system catalog
- **Client setup** for Claude Code, Claude Desktop, Cursor, VS Code, Zed, Continue, and Windsurf (`mcp-client-connect.md`)
- **Diagnostic workflows** for common troubleshooting scenarios
- **Remediation runbooks** with copy-pasteable SQL commands
- **Guardrails** against known pitfalls (cluster-scoped introspection reads, per-process replica relations, clusters without replicas)

## Setup

1. Install the skill:

   ```bash
   npx skills add MaterializeInc/agent-skills
   ```

2. Connect your MCP client to the Materialize developer endpoint. See the
   [MCP Server for Developers](https://materialize.com/docs/integrations/mcp-server/mcp-developer/)
   documentation for connection instructions.
