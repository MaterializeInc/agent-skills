# MCP Servers and agent skills

This section contains guides for installing Materialize Agent skills and integrating with Materialize's built-in MCP servers.

## Agent skills

Materialize provides open-source [agent
skills](https://github.com/MaterializeInc/agent-skills) that give coding agents
like Claude Code, Codex, and Cursor access to Materialize documentation and
reference material. For the list of available skills and installation
instructions, see [Agent Skills](/developer-tools/mcp-server/coding-agent-skills/).

## MCP servers

Materialize provides built-in Model Context Protocol (MCP) servers that AI
agents can use. The MCP interface is served directly by the database; no sidecar
process or external server is required. These endpoints use [JSON-RPC
 2.0](https://www.jsonrpc.org/specification) over HTTP POST (default port 6876)
and support the MCP `initialize`, `tools/list`, and `tools/call` methods.

| Endpoint | Path | Description |
|----------|------|-------------|
| **Agent** | `/api/mcp/agent` | Discover and query your real-time data products over HTTP. <br>For details, see [MCP Server for agents](/developer-tools/mcp-server/mcp-agent/).<br>*Available starting in v26.24*|
| **Developer** | `/api/mcp/developer` | Read `mz_*` system catalog tables for troubleshooting and observability, and run queries on your objects. <br>For details, see [MCP Server for developer](/developer-tools/mcp-server/mcp-developer/). <br>*Available starting in v26.20*|

## See also

- [Use an ontology table](/transform-data/patterns/ontology/) to curate join
  relationships that agents query through the `query` tool before writing
  multi-table SQL.
- [MCP Server
  Troubleshooting](/developer-tools/mcp-server/mcp-server-troubleshooting/)

## Pages in this section

- [Agent endpoint configuration](/developer-tools/mcp-server/mcp-agent-config/index.md): Configuration for /api/mcp/agent endpoint.
- [Agent MCP server tools](/developer-tools/mcp-server/mcp-agent-tools/index.md): Tools exposed by the `materialize-agent` MCP server.
- [Agent Skills](/developer-tools/mcp-server/coding-agent-skills/index.md): Add Materialize skills to coding agents like Claude Code, Codex, Cursor, and others.
- [Developer endpoint configuration](/developer-tools/mcp-server/mcp-developer-config/index.md): Configuration for /api/mcp/developer endpoint.
- [Developer MCP server tools](/developer-tools/mcp-server/mcp-developer-tools/index.md): Tools exposed by the `materialize-developer` MCP server.
- [MCP Server for Agents](/developer-tools/mcp-server/mcp-agent/index.md): Query data products via Materialize's built-in materialize-agent MCP Server.
- [MCP Server for Developers and Operators](/developer-tools/mcp-server/mcp-developer/index.md): Query Materialize system catalog tables for troubleshooting and observability via the built-in materialize-developer MCP server.
- [MCP Server Troubleshooting](/developer-tools/mcp-server/mcp-server-troubleshooting/index.md): Troubleshooting guide for the MCP Server.
