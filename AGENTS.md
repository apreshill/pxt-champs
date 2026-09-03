# AGENTS.md

You are helping someone use Pixeltable Cloud. Pixeltable is an OLTP database for multimodal AI:
media, its AI outputs, and app state live in one hosted database at `pxt://<org>:<db>`.

## Start here

- Add the skill: `npx skills add pixeltable/pixeltable-skill`. Docs: https://docs.pixeltable.com
  (any page takes a `.md` suffix, e.g. https://docs.pixeltable.com/platform/cli.md). Do not guess APIs.
- Building an app for the user: follow `AGENT_PROMPT.md` and `CLOUD_QUICKSTART.md`.

## The flow

`pxt <noun> <verb>`. Nouns `db` / `schema` / `service`; the reconcile verbs are `diff` (preview) and
`update` (apply). Deploying an app:

```bash
pxt db update  <db> -f          # create the db, build its image (first run: several minutes)
pxt schema update  app.py <db>  # create the tables
pxt service update app.py <db> -f
```

Write the app as a class-based schema (`TableModel` + `FastAPIRouter`) from `pxt service example --out
app.py`; keep that shape. Prompt the user to open `pxt dashboard` to watch tables and computed columns
fill in.

## Anti-patterns

Pixeltable replaces these; reaching for them means you are off-path.

- No LangChain / vector database / pandas as a store / per-row model loops. Chunk with an iterator,
  search with `.similarity()`, compute with a computed column.

## CLI reality

- `pxt db update` and `pxt service update` prompt; always pass `-f`.
- There is no `pxt db create` (use `db update`) and no `pxt ls -r` (use `pxt ls --tree`).
- Cloud state is `pxt ls --tree` and `pxt db status`, not `pxt status` (that is the local daemon).
- Add `--json` to inspection commands. Read the org from `pxt org list`; do not hardcode it.
- Exit codes: 0 agree, 2 pending, 3 refused (needs `-f` / `--allow-destructive`), 1 error.
