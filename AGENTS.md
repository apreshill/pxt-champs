# AGENTS.md

Pixeltable is an OLTP database for multimodal AI. You declare tables and computed columns as a
class-based schema and define a service over them in one `app.py`, then create and serve it with the
`pxt` CLI — locally, or in the cloud with the same commands.

- Add the skill for the schema DSL: `npx skills add pixeltable/pixeltable-skill`. The SDK API reference
  is at https://docs.pixeltable.com/sdk/latest/pixeltable.
- The CLI is a `pxt <noun> <verb>` grammar; `schema`, `service`, and `db` share `diff` and `update`. Run
  `pxt <noun> --help` rather than guessing. Docs: https://docs.pixeltable.com (any page takes a `.md`
  suffix).
- Cloud deploy follows the [Pixeltable Cloud guide](https://github.com/pixeltable/pixeltable/blob/main/docs/release/cloud.mdx). A `pxt login` session is enough. Keep the local database entry and add a second one, `pxt://<org>:main`, unless `main` already has another project. Order is `pxt db update`, then `pxt schema update`, then `pxt service update`. Hosted HTTP needs `X-api-key`. `pxt service run` is local only. Copy the URL from `pxt service list`.

To build an app, follow `guides/build-an-app.md`.
