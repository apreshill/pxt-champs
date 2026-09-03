# Cloud quickstart: build your own app on a hosted database

Against pixeltable 0.7.4. The CLI is a `pxt <noun> <verb>` grammar; the reconcile verbs are
`pxt db {diff,update}`, `pxt schema {diff,update,prune}`, and `pxt service {diff,update,prune}`. Full
CLI reference: https://docs.pixeltable.com/platform/cli.md (any docs URL takes a `.md` suffix).

## 1. Create a Python environment (pick one)

The project directory must end up with a lockfile at its root, because `pxt db update` builds the
hosted image from it.

| lockfile           | how the image installs it                    | note |
|--------------------|----------------------------------------------|------|
| `uv.lock`          | `uv sync --frozen`                           | `pixeltable` must be a dependency in `pyproject.toml` |
| `requirements.txt` | `pip install -r requirements.txt`            | must list `pixeltable[serve]` |
| `poetry.lock`      | `poetry install --only main --no-root`       | `pixeltable` must be a main dependency |
| none               | `pip install 'pixeltable[serve]'` (latest)   | the CLI warns; nothing else from your env ships |

Python 3.11+. The image python is `python_version` from your config, otherwise the interpreter that
ran `pxt db update`.

```bash
mkdir ~/my-pxt-app && cd ~/my-pxt-app
uv init --bare && uv add 'pixeltable[serve]'   # writes pyproject.toml + uv.lock
source .venv/bin/activate
pxt --version                                  # pxt 0.7.4
```

## 2. Declare the hosted database

In the project root, add the entry to `pyproject.toml` (this also marks the directory as the project
root). Set your org slug from `pxt org list`.

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:<your-db>'
# python_version = '3.12'
# system_dependencies = ['ffmpeg']              # OS packages baked into the image
# secrets.openai_api_key = 'env:OPENAI_API_KEY' # read from your env at `pxt db update`
# workers = 1  cpu = 2.0  memory_mb = 4096  disk_gb = 50
```

Add a `.gitignore` with `.venv/` so it is not packaged into the image.

## 3. Write the app

```bash
pxt service example --out app.py   # a class-based schema + a FastAPIRouter, ready to edit
pxt service check app.py           # "app.py: valid"
```

Keep the class-based shape (`TableModel` + `FastAPIRouter`) the scaffold gives you. Edit it into your
app: computed columns for model calls, views/iterators to split video/audio/documents, an embedding
index for search.

## 4. Create the database and ship the project

`db update` and `service update` prompt before applying; pass `-f` to skip the prompt.

```bash
pxt db diff       pxt://<your-org>:<your-db>        # read-only plan
pxt db update  -f pxt://<your-org>:<your-db>        # create db, build image (first run: several minutes)
pxt db status     pxt://<your-org>:<your-db> --json # wait for "state": "AVAILABLE"

pxt schema update  app.py pxt://<your-org>:<your-db>    # create the tables
pxt service update app.py pxt://<your-org>:<your-db> -f # start the services
pxt service list          pxt://<your-org>:<your-db>    # prints the service URL

curl -X POST https://<your-org>-<your-db>.svc.pxt.run/<service>/<route> \
  -H 'Content-Type: application/json' -d '{ ... }'
```

Open the dashboard to browse tables, media, and column lineage: `pxt dashboard`
(https://docs.pixeltable.com/platform/dashboard.md).

## 5. The edit loop

```bash
# change app.py, then:
pxt db update  -f pxt://<your-org>:<your-db>            # re-ship the project (rebuilds image only if deps changed)
pxt schema update  app.py pxt://<your-org>:<your-db>    # add --allow-destructive for column drops
pxt service update app.py pxt://<your-org>:<your-db> -f # restarts changed services
```

Exit codes across reconcile verbs: 0 in agreement, 2 changes pending, 3 refused (needs
`--allow-destructive` or `-f`), 1 error.

Secrets for LLM apps: `secrets.* = 'env:VAR'` in the config, or
`pxt secret set pxt://<your-org>:<your-db> OPENAI_API_KEY=sk-...`.

Clean up: `pxt db stop pxt://<your-org>:<your-db>` (keeps storage), `pxt db delete ...` (irreversible).

## 6. Exit codes and expected output

- `pxt schema check app.py` → `app.py: valid` (exit 0).
- `pxt schema diff app.py <db>` → the create plan (exit 2 when changes are pending).
- `pxt schema update app.py <db>` → `created <db>/<table>` (exit 0).
- `pxt db update <db>` → builds the image (first run: several minutes), ends `applied  AVAILABLE` (exit 0).
- Service URL: `https://<org>-<db>.svc.pxt.run/<service>`.
- Across reconcile verbs: 0 in agreement, 2 changes pending, 3 refused, 1 error.
