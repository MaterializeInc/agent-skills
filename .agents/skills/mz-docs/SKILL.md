---
name: mz-docs
description: Materialize documentation for SQL syntax, data ingestion, concepts, and best practices, fetched live as markdown from materialize.com. Use when users ask about Materialize queries, sources, sinks, views, indexes, clusters, or any other Materialize feature.
allowed-tools: WebFetch(domain:materialize.com)
---

# Materialize Documentation

Answer Materialize questions from the current docs, not from memory. Every docs page is published as markdown.

1. **Find the page in [`llms.txt`](https://materialize.com/docs/llms.txt).** It lists every page with its title, markdown URL and a one-line description. Fetch it and ask for the pages about your topic, with their URLs exactly as written. Do not guess URLs: only `https://materialize.com/docs/markdown-docs/<path>/index.md` serves markdown.
2. **Fetch the page's markdown URL** with WebFetch, or your agent's fetch tool. WebFetch returns another model's extract, not the page, so ask for the syntax, query or table you need by name and verbatim. If you have a shell, `curl -sf <url>` returns the whole page.
3. **Do not fetch section pages.** A page is a section page when `llms.txt` lists other pages below its path: `sql/index.md` is the section page for `sql/create-source/index.md`. Section pages include the full text of every page below them and are too long to fetch whole. Fetch the pages below them instead.
4. **Convert links before following them.** Links in the pages omit the `markdown-docs` prefix:
   - `/sql/create-cluster` or `/sql/create-cluster/#syntax`: fetch `https://materialize.com/docs/markdown-docs/sql/create-cluster/index.md`.
   - `../create-role` on `.../markdown-docs/sql/alter-role/index.md`: fetch `.../markdown-docs/sql/create-role/index.md`.
   - If a converted URL returns 404, find the page in `llms.txt` by the link text.
5. **Answer** with SQL syntax quoted exactly as the page gives it, and link the human-readable page: drop `markdown-docs/` and the trailing `index.md`, for example `https://materialize.com/docs/sql/create-source/`.
