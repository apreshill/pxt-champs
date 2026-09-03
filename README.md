# pxt-champs: Pixeltable Cloud quickstart

Cloud-hosted tables, for beta testers. This repo takes you from nothing to a working multimodal
database in the cloud in under 30 minutes. You do not need to know Pixeltable already.

## What Pixeltable is

An OLTP database for multimodal AI apps. Your media (images, audio, video, documents), the AI
outputs you derive from it, and your app state live in one database and stay consistent as data
changes. Pixeltable Cloud hosts that database for you, addressed as `pxt://<your-org>:<db>`.
`CHEATSHEET.md` is a one-page command reference to keep handy.

## What you need

- Python 3.11 or newer, and [uv](https://docs.astral.sh/uv/).
- Access to the closed beta, through your invite or the waitlist.
- An API key: once you have access, sign in to the dashboard, create an org (it comes with a `main`
  database), open API Keys, create one, and copy it. You see it once.

## Setup

With this repo cloned (needed for the notebooks, `app.py`, and sample data):

```bash
uv sync
```

Just want the library and CLI, without cloning? Install Pixeltable straight from PyPI:

```bash
pip install 'pixeltable[serve]'      # or: uv pip install 'pixeltable[serve]'
```

Give Pixeltable your key. Persistent, in `~/.pixeltable/config.toml`:

```toml
[pixeltable]
api_key = 'your-api-key'
```

Or per session: `export PIXELTABLE_API_KEY=your-api-key` (see `.env.example`). Details:
https://docs.pixeltable.com/platform/configuration

## The path

Run these in order. The first two are the whole point.

1. `01_setup.ipynb`: reach your cloud database and confirm it is live.
2. `02_cloud_tables.ipynb` (or read `CLOUD_TABLES.md`): declare a multimodal schema in the cloud, insert
   postcards, and watch the database compute. This is the one that matters.
3. `03_serve_api.ipynb`: serve your cloud database as an HTTP API.
4. `04_image_search.ipynb`: search your postcard images by a text query. Optional, and it
   installs a large model (`uv sync --extra clip`, ~600MB download).
5. `05_share_table.ipynb`: publish a table and let someone else read it. Optional.

## Build your own app

Ready to ship a whole app of your own (its own dependencies, its own hosted database and services)?
`CLOUD_QUICKSTART.md` is the tight, agent-friendly reference for that: pick a Python environment,
declare a database, and use the `pxt db` / `pxt schema` / `pxt service` `diff`/`update` loop.

## Using an agent

Point your agent at `AGENTS.md`. It carries the mental model, equips the agent, routes it, and lists
the command traps so it does not waste your time. Everything in this repo is built to be driven by an
agent.

## Links

- Docs: https://docs.pixeltable.com
- Agent skill: `npx skills add pixeltable/pixeltable-skill`
- Stuck? `TROUBLESHOOTING.md`
