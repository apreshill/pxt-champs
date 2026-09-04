# AGENTS.md

Pixeltable is an OLTP database for multimodal AI. Media, the AI outputs derived from it, and app state
live in one hosted database at `pxt://<org>:<db>`; you declare the tables and computed columns as a
class-based schema, and the database maintains them. This file is the reference for building and
deploying an app on it. To build one, follow `guides/build-an-app.md`.

- Add the skill for the schema DSL: `npx skills add pixeltable/pixeltable-skill`. The SDK API reference
  is at https://docs.pixeltable.com/sdk/latest/pixeltable (the `Table` class at
  https://docs.pixeltable.com/sdk/latest/table).
- The CLI is a `pxt <noun> <verb>` grammar; the reconcile verbs are `pxt db {diff,update}`,
  `pxt schema {diff,update,prune}`, and `pxt service {diff,update,prune}`. Run `pxt <noun> --help` for a
  noun's verbs rather than guessing. Docs: https://docs.pixeltable.com (any page takes a `.md` suffix).

Against pixeltable 0.7.5.

## 1. Declare the hosted database

In the project root, add the entry to `pyproject.toml` (this also marks the directory as the project
root). Set your org slug from `pxt org list`; `pxt db update` builds the hosted image from the project's
lockfile.

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:<your-db>'
# python_version = '3.12'
# system_dependencies = ['ffmpeg']              # OS packages baked into the image
# secrets.openai_api_key = 'env:OPENAI_API_KEY' # read from your env at `pxt db update`
# workers = 1  cpu = 2.0  memory_mb = 4096  disk_gb = 50
# include = ['app/**']  exclude = ['.venv']     # what gets packaged; default: everything git ignores is left out
```

Add a `.gitignore` with `.venv/` so it is not packaged into the image.

## 2. Write the app

```bash
pxt service example --out app.py   # a class-based schema + a FastAPIRouter, ready to edit
pxt service check app.py           # validates the file, no database: "app.py: valid"
```

The generated file defines a `docs` table (`doc_id`, `title`, `body`), two computed columns, and a
**service named `ingest`** with two **routes**, `POST /docs` (insert) and `POST /titles` (compute).
Keep the class-based shape (`TableModel` + `FastAPIRouter`); edit it into your app. A table's `name=`
sets its path in the catalog (not the class name); `FastAPIRouter(name=...)` sets the service name;
each route's `path=` sets its URL path.

## 3. Create the database and ship the project

`db update` and `service update` prompt before applying; pass `-f` to skip the prompt.

```bash
pxt db diff       pxt://<your-org>:<your-db>        # read-only plan
pxt db update  -f pxt://<your-org>:<your-db>        # create db, build image (first run: several minutes)
pxt db status     pxt://<your-org>:<your-db> --json # wait for "state": "AVAILABLE"

pxt schema update  app.py pxt://<your-org>:<your-db>    # create the tables
pxt service update app.py pxt://<your-org>:<your-db> -f # start the services
pxt service list          pxt://<your-org>:<your-db>    # prints each service's URL and its routes
```

A service URL has four parts, from three places:

| part | you set it in | example |
|------|---------------|---------|
| org | `pxt org list` | `goldener` |
| db | `pyproject.toml`, the `[[tool.pixeltable.database]]` `name` | `beta-test` |
| service | `app.py`, `FastAPIRouter(name=...)` | `ingest` |
| route | `app.py`, the route's `path=...` | `/docs` |

They assemble as `https://<org>-<db>.svc.pxt.run/<service>/<route>`. Do not build it by hand:
`pxt service list` prints the whole URL and the routes.

```bash
curl -X POST https://goldener-beta-test.svc.pxt.run/ingest/docs \
  -H 'Content-Type: application/json' -d '{"doc_id": 1, "title": "hello", "body": null}'
```

Open the dashboard to browse tables, media, and column lineage: `pxt dashboard`.

## 4. The edit loop

Edit `app.py`, then ship and apply:

```bash
pxt db update  -f pxt://<your-org>:<your-db>            # re-ship app.py (rebuilds image only if deps changed)
pxt schema update  app.py pxt://<your-org>:<your-db>    # adds new columns
pxt service update app.py pxt://<your-org>:<your-db> -f # restarts changed services
```

Adding a column is safe. You cannot *alter* an existing column's definition — reconcile reports it as
`unsupported`; to change one, drop it (`--allow-destructive`) and add it back. `update` never removes;
to drop what you deleted from `app.py`, prune it:

```bash
pxt schema  prune app.py pxt://<your-org>:<your-db> -n   # preview the drops, then -f
pxt service prune app.py pxt://<your-org>:<your-db> -n   # stops services app.py no longer declares
```

Exit codes across reconcile verbs: 0 in agreement, 2 changes pending, 3 refused (needs
`--allow-destructive` or `-f`), 1 error.

Secrets for provider calls: `secrets.* = 'env:VAR'` in the config, or
`pxt secret set pxt://<your-org>:<your-db> OPENAI_API_KEY=sk-...`.

Clean up: `pxt db stop pxt://<your-org>:<your-db>` (keeps storage), `pxt db delete ...` (irreversible).

## Gotchas

- **Pass the full `pxt://` URI to every `pxt db` command.** Its help says the URI can default to a
  `db_uri` config setting, separate from your `[[tool.pixeltable.database]]` entry, so name it
  explicitly.
- **Declare the database in one file only.** If both `pyproject.toml` (`[[tool.pixeltable.database]]`)
  and a `pixeltable.toml` (`[[pixeltable.database]]`) declare it, `pixeltable.toml` wins silently.
- **`pxt db update` rebuilds the image only when it must** — when the lockfile, `python_version`, or
  `system_dependencies` changed. The first build takes several minutes; a later source-only edit uploads
  in seconds.
- **A running database keeps the secrets it started with.** After changing a secret, `pxt db stop` then
  `pxt db start` to pick it up.
