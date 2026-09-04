# pxt-champs

Pixeltable is an OLTP database for multimodal AI. Your media, the AI outputs you derive from it, and
your app's state live in one database that keeps them consistent as data changes. You declare a schema,
insert data, and query it — like any database, but one that stores multimodal data and orchestrates the
models and transforms that populate it.

This repo is a beta-tester quickstart for **cloud-hosted tables**: the Pixeltable database you'd run
locally, now running on hosted infrastructure and addressed by a `pxt://<your-org>:<db>` URI. Hosted, it becomes a database you can build an app on:

- **serve** your tables over HTTP — built-in FastAPI routes;
- **query and experiment** with the Pixeltable SDK and CLI — the same API as a local database;
- **share** one live copy with your team — concurrent reads and writes.

The hosted database runs on managed infrastructure that stays always on — nothing for you to provision,
scale, or operate.

## Environment

Requires **Python 3.11+** and **`pixeltable[serve]` 0.7.5** (this repo pins it). Pixeltable pulls
~500MB, so install ahead of a jam session.

**For the jam session** — install [uv](https://docs.astral.sh/uv/), then clone this repo:

```bash
git clone https://github.com/apreshill/pxt-champs && cd pxt-champs
uv sync
```

**For your own app** — start a fresh project (any manager below; `pixeltable` must be a dependency, and
the project needs a lockfile at its root, since `pxt db update` builds the hosted image from it):


| manager          | commands                                                                                                                       | lockfile           |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------ |
| uv (recommended) | `uv init --bare && uv add 'pixeltable[serve]'`                                                                                 | `uv.lock`          |
| venv + pip       | `python3 -m venv .venv && source .venv/bin/activate && pip install 'pixeltable[serve]' && pip freeze > requirements.txt`       | `requirements.txt` |
| conda            | `conda create -n app python=3.12 -y && conda activate app && pip install 'pixeltable[serve]' && pip freeze > requirements.txt` | `requirements.txt` |
| poetry           | `poetry init -n && poetry add 'pixeltable[serve]'`                                                                             | `poetry.lock`      |


Make sure `pxt` resolves to the one you installed (`which pxt`); another venv or conda base on PATH
can shadow it. Confirm the version:

```bash
pxt --version    # pxt 0.7.5
```

## API key

Get a key from the Cloud dashboard: https://www.pixeltable.com/dashboard
- If you don't have an account, choose a way to sign up; if you do, you can sign in from the same page
- Create a new key that starts with `'sk_…'`

Store your API key one of two ways:

**In a config file** — `~/.pixeltable/config.toml`:

```toml
[pixeltable]
api_key = 'your-api-key'
```

**Per session** — `export PIXELTABLE_API_KEY=your-api-key`. Details:
[https://docs.pixeltable.com/platform/configuration.md](https://docs.pixeltable.com/platform/configuration.md). Confirm it, and note your org slug:

```bash
uv run pxt config      # pixeltable.api_key shows <redacted>
uv run pxt org list    # your org slug, used in every pxt:// URI
```



## Where to go next

- **A guided jam session, about 20 minutes:** `JAM.md` — create a hosted database, declare a table,
  insert a row, and serve it over HTTP, one step at a time. Start here.
- **Build your own app:** follow `CLOUD_QUICKSTART.md` yourself, or hand `AGENT_PROMPT.md` to your
  coding agent — it works from that same quickstart.



## Links

Docs [https://docs.pixeltable.com](https://docs.pixeltable.com) · Dashboard [https://docs.pixeltable.com/platform/dashboard.md](https://docs.pixeltable.com/platform/dashboard.md)