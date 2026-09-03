# Cloud quickstart: build your own app on a hosted database

The tight version, for when you want to ship your own app to Pixeltable Cloud rather than follow the
postcards notebooks. Written against pixeltable 0.7.4. The CLI is a `pxt <noun> <verb>` grammar; the
reconcile verbs are `pxt db {diff,update}`, `pxt schema {diff,update,prune}`, and
`pxt service {diff,update,prune}`.

## 1. Create a Python environment (pick one)

Whatever you pick, the project directory must end up with a lockfile at its root, because
`pxt db update` builds the hosted image from it.

| lockfile           | how the image installs it                           | note |
|--------------------|-----------------------------------------------------|------|
| `uv.lock`          | `uv sync --frozen`                                  | `pixeltable` must be a dependency in `pyproject.toml` |
| `requirements.txt` | `pip install -r requirements.txt`                   | must list `pixeltable[serve]`; authoritative for the version |
| `poetry.lock`      | `poetry install --only main --no-root`              | `pixeltable` must be a main dependency |
| none               | `pip install 'pixeltable[serve]'` (latest)          | the CLI warns; nothing else from your env is installed |

Python 3.11+ works. The image python is `python_version` from your `pixeltable.toml`, otherwise the
interpreter that ran `pxt db update`.

### uv project (recommended)

```bash
mkdir ~/my-pxt-app && cd ~/my-pxt-app
uv init --python 3.14 --bare      # writes pyproject.toml only
uv add 'pixeltable[serve]'        # creates .venv and uv.lock
source .venv/bin/activate
pxt --version                     # pxt 0.7.4
```

### venv + pip

```bash
mkdir ~/my-pxt-app && cd ~/my-pxt-app
python3.12 -m venv .venv && source .venv/bin/activate
pip install 'pixeltable[serve]'
pip freeze > requirements.txt     # or hand-write: pixeltable[serve]==0.7.4
```

### conda (make a NEW env)

```bash
conda create -n my-pxt-app python=3.12 pip -y && conda activate my-pxt-app
mkdir ~/my-pxt-app && cd ~/my-pxt-app
pip install 'pixeltable[serve]'
pip freeze > requirements.txt     # required: the image never sees your conda env
```

Make sure `pxt` resolves to the one you installed (`which pxt`); a conda base or another venv on PATH
can shadow it. Check `pxt --help`: the `db` line reads
`diff/update/create/list/status/start/stop/build-image/delete`.

## 2. Set your API key

From the dashboard (API Keys, shown once). Persistent, in `~/.pixeltable/config.toml`:

```toml
[pixeltable]
api_key = 'your-api-key'
```

Or per session: `export PIXELTABLE_API_KEY=your-api-key`. Confirm with `pxt config` and `pxt org list`
(the second prints your org slug, which you use in every `pxt://` URI below). Details:
https://docs.pixeltable.com/platform/configuration.

## 3. Declare the hosted database

In the project root, add a `[[tool.pixeltable.database]]` entry to `pyproject.toml` (or a
`pixeltable.toml`; if both exist, `pixeltable.toml` wins). The entry marks the directory as the
project root, so every folder under it that holds Python must be a valid identifier.

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:<your-db>'
# python_version = '3.12'                        # default: the interpreter running pxt
# system_dependencies = ['ffmpeg']               # conda-forge packages baked into the image
# secrets.openai_api_key = 'env:OPENAI_API_KEY'  # read from your env at `pxt db update`
# workers = 1  cpu = 2.0  memory_mb = 4096  disk_gb = 50
# include = ['app/**']  exclude = ['.venv', '*.pyc']   # default: everything git would not ignore
```

Add a `.gitignore` with `.venv/` so the venv is not packaged into the project archive.

## 4. Write the app

```bash
pxt service example --out app.py   # models + a FastAPIRouter with example routes
pxt service check app.py           # "app.py: valid" (imports it in the local daemon)
```

The generated file defines a table, two computed columns (one via a `@pxt.udf`), and a service with
an insert route and a compute route. Edit it or swap in your own `fastapi.FastAPI` object.

## 5. Create the database and ship the project

```bash
pxt db diff   pxt://<your-org>:<your-db>   # read-only plan; the database will be created
pxt db update pxt://<your-org>:<your-db>   # first run: create db, build image, upload archive
```

Order inside `update`: secrets, then the image (only when the lockfile, `python_version`,
`system_dependencies`, or the pixeltable version changed), then the project archive (when any selected
file changed), then one resize. **The first image build takes 10+ minutes**; a later source-only edit
uploads in seconds. Wait for `pxt db status` to read `AVAILABLE`.

Then create the tables and start the service in the hosted database:

```bash
pxt schema  update app.py pxt://<your-org>:<your-db>
pxt service update app.py pxt://<your-org>:<your-db>
pxt service list          pxt://<your-org>:<your-db>   # prints the service URL
curl -X POST <service url>/docs -H 'Content-Type: application/json' \
     -d '{"doc_id": 1, "title": "hello pixeltable cloud", "body": null}'
pxt rows pxt://<your-org>:<your-db>/docs
```

## 6. The edit loop

```bash
# change app.py, then:
pxt db diff       pxt://<your-org>:<your-db>          # exit 2 = something to ship
pxt db update     pxt://<your-org>:<your-db>          # archive only, unless deps changed
pxt schema diff   app.py pxt://<your-org>:<your-db>   # exit 2 = drift
pxt schema update app.py pxt://<your-org>:<your-db>   # add --allow-destructive for drops
pxt service diff   app.py pxt://<your-org>:<your-db>
pxt service update app.py pxt://<your-org>:<your-db>  # restarts changed services
pxt schema  prune app.py pxt://<your-org>:<your-db> -n   # dry-run first, then -f
```

Exit codes across all reconcile verbs: 0 in agreement, 2 changes pending, 3 refused (needs
`--allow-destructive` or `-f`), 1 error.

Secrets for LLM apps: either the `secrets.* = 'env:VAR'` line in the config, or
`pxt secret set pxt://<your-org>:<your-db> OPENAI_API_KEY=sk-...`. A running database keeps the values
it started with; `pxt db stop` then `pxt db start` picks up changes.

Clean up when done:

```bash
pxt service stop <name>                     # or: pxt service prune app.py pxt://... -f
pxt db stop   pxt://<your-org>:<your-db>    # releases compute, keeps storage
pxt db delete pxt://<your-org>:<your-db>    # irreversible
```
