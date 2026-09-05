# AGENTS.md

Pixeltable is an OLTP database for multimodal AI. You declare tables and computed columns as a
class-based schema and define a service over them in one `app.py`, then create and serve it with the
`pxt` CLI — locally, or in the cloud with the same commands.

- Add the skill for the schema DSL: `npx skills add pixeltable/pixeltable-skill`. The SDK API reference
  is at https://docs.pixeltable.com/sdk/latest/pixeltable.
- The CLI is a `pxt <noun> <verb>` grammar; `schema`, `service`, and `db` share `diff` and `update`. Run
  `pxt <noun> --help` rather than guessing. Docs: https://docs.pixeltable.com (any page takes a `.md`
  suffix).

To build an app, follow `guides/build-an-app.md`.
