# mz-docs

Documentation retrieval and synthesis for Materialize.

## Intended use cases

- Answer “how do I …?” questions with references to Materialize documentation.
- Produce task-focused runbooks and checklists (e.g., upgrade steps, configuration guidance).
- Generate concise summaries from long documentation snippets.

## Inputs

- User question / task
- Optional context:
  - Materialize version
  - SaaS vs self-hosted
  - Links/snippets/log excerpts

## Outputs

- A structured answer with explicit assumptions and (when available) citations to provided references.

The skill does not bundle the docs. It fetches the current markdown rendition of each page from materialize.com.

See `SKILL.md` for canonical behavior and constraints.
