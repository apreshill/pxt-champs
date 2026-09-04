# Cloud quickstart: build your own app on a hosted database

Against pixeltable 0.7.5. The CLI is a `pxt <noun> <verb>` grammar; the reconcile verbs are
`pxt db {diff,update}`, `pxt schema {diff,update,prune}`, and `pxt service {diff,update,prune}`. Run
`pxt <noun> --help` for a noun's verbs rather than guessing. Full CLI reference:
https://docs.pixeltable.com/platform/cli.md (any docs URL takes a `.md` suffix).

Setup (environment and API key) is in the README. Work in your project directory; `pxt db update`
builds the hosted image from its lockfile.

## 1. Declare the hosted database

In the project root, add the entry to `pyproject.toml` (this also marks the directory as the project
root). Set your org slug from `pxt org list`.

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

A service URL has four parts, and they come from three places:

| part | you set it in | example |
|------|---------------|---------|
| org | `pxt org list` | `goldener` |
| db | `pyproject.toml`, the `[[tool.pixeltable.database]]` `name` | `beta-test` |
| service | `app.py`, `FastAPIRouter(name=...)` | `ingest` |
| route | `app.py`, the route's `path=...` | `/docs` |

They assemble as `https://<org>-<db>.svc.pxt.run/<service>/<route>`. You do not build it by hand:
`pxt service list` prints the whole URL and the routes, so copy it from there.

```
pxt://goldener:beta-test/ingest   https://goldener-beta-test.svc.pxt.run/ingest   AVAILABLE   app.py
    POST  /docs     insert    in: doc_id, title, body   out: title_upper
    POST  /titles   compute   in: title                 out: title_upper
```

```bash
curl -X POST https://goldener-beta-test.svc.pxt.run/ingest/docs \
  -H 'Content-Type: application/json' -d '{"doc_id": 1, "title": "hello", "body": null}'
```

Open the dashboard to browse tables, media, and column lineage: `pxt dashboard`
(https://docs.pixeltable.com/platform/dashboard.md).

## 4. The edit loop

Edit `app.py`. For example, add a computed column to `Docs`:

```python
    summary = pxtf.string.slice(body, 0, 80)   # a new computed column
```

Adding a column is safe. If you *rename* one, update every reference to it too (route `outputs=`,
other computed columns), or `app.py` fails to load with `has no attribute '<old-name>'`.

Then ship the change and apply it:

```bash
pxt db update  -f pxt://<your-org>:<your-db>            # re-ship app.py (rebuilds image only if deps changed)
pxt schema update  app.py pxt://<your-org>:<your-db>    # adds the new column (--allow-destructive to drop one)
pxt service update app.py pxt://<your-org>:<your-db> -f # restarts changed services
```

`update` adds and changes, but never removes. To drop what you deleted from `app.py`, prune it (`-n`
previews, `-f` applies):

```bash
pxt schema  prune app.py pxt://<your-org>:<your-db> -n   # preview the drops, then -f
pxt service prune app.py pxt://<your-org>:<your-db> -n   # stops services app.py no longer declares
```

Exit codes across reconcile verbs: 0 in agreement, 2 changes pending, 3 refused (needs
`--allow-destructive` or `-f`), 1 error.

Secrets for LLM apps: `secrets.* = 'env:VAR'` in the config, or
`pxt secret set pxt://<your-org>:<your-db> OPENAI_API_KEY=sk-...`.

Clean up: `pxt db stop pxt://<your-org>:<your-db>` (keeps storage), `pxt db delete ...` (irreversible).

## Gotchas

- **Pass the full `pxt://` URI to every `pxt db` command.** Its help says the URI can default to a
  `db_uri` config setting, separate from your `[[tool.pixeltable.database]]` entry, so name it
  explicitly.
- **Declare the database in one file only.** If both `pyproject.toml` (`[[tool.pixeltable.database]]`)
  and a `pixeltable.toml` (`[[pixeltable.database]]`) declare it, `pixeltable.toml` wins silently.
- **`pxt db update` rebuilds the image only when it must.** It applies secrets, rebuilds the image only
  if the lockfile, `python_version`, or `system_dependencies` changed, uploads the project archive when
  any file changed, then resizes. The first image build takes several minutes; a later source-only edit
  uploads in seconds.
- **A running database keeps the secrets it started with.** After changing a secret, `pxt db stop` then
  `pxt db start` to pick it up.
