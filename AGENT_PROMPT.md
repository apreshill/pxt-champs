# Build a Pixeltable Cloud app with your agent

Don't want to click through the notebooks? Fill in the two brackets below and hand this whole file to
your coding agent (Claude Code, Cursor, etc.). It builds and deploys a real app on your cloud
database, then tells you the URL.

---

You are building a real application on Pixeltable Cloud and deploying it to a hosted database. Read
`AGENTS.md` and `CLOUD_QUICKSTART.md` in this repo first, and follow the quickstart as your reference
for every `pxt` command. Add the API reference with `npx skills add pixeltable/pixeltable-skill`.

## What to build

**<Describe the app in a sentence or two. For example: "A table of PDFs where each row gets a
computed summary from GPT-4o-mini and an embedding index, plus a POST /ingest endpoint and a GET
/search endpoint that finds passages by a text query.">**

Keep it a single-file FastAPI + Pixeltable app (`app.py`) unless I say otherwise. Start from
`pxt service example --out app.py` and rewrite it into the app above. Use computed columns for the
model calls, an embedding index for search, and views/iterators to chunk documents, video, or audio.
Do not reach for LangChain, a separate vector database, pandas as a store, or per-row Python loops
over a model. Those are what Pixeltable replaces.

## Setup

- Python 3.11 or newer. Use a `uv` project (quickstart Option A) unless I tell you otherwise, so the
  project has a `uv.lock` at its root. `pxt db update` builds the hosted image from that lockfile.
- My Pixeltable Cloud API key is already in `~/.pixeltable/config.toml`. Confirm with `pxt config`
  (my `pixeltable.api_key` shows `<redacted>`) and get my org slug from `pxt org list`.
- My org slug: **<your-org>**. Use it in every `pxt://` URI. Never touch a database you did not create.

## Build and ship

Follow the quickstart in order:

1. Declare the database in `pyproject.toml`: `[[tool.pixeltable.database]] name = 'pxt://<your-org>:<pick-a-db-name>'`.
2. `pxt db diff` then `pxt db update` to create it and build the image. The first build takes 10+
   minutes; wait for `pxt db status` to read `AVAILABLE`.
3. `pxt schema update app.py pxt://<your-org>:<db>` to create the tables, then
   `pxt service update app.py pxt://<your-org>:<db>` to serve the routes.
4. `pxt service list` for the URL, then `curl` an endpoint to prove it works end to end.

If any computed column calls a provider (OpenAI, Gemini, etc.), give the hosted database the key both
ways the quickstart shows: `secrets.* = 'env:VAR'` in the config, and `pxt secret set`. Use cheap
models (`gpt-4o-mini` or similar).

## Iterate

When you change `app.py`, run the reconcile loop: `pxt schema diff` / `pxt service diff` (exit code 2
means something to ship), then `update`. Adding a column is additive; dropping one needs
`--allow-destructive`.

## When you're done, tell me

- What you built: the tables, the computed columns, the endpoints.
- The live service URL, and one `curl` (or short Python) call that works, with its output.
- Anything that surprised you, errored, or contradicted the docs, with the exact command and output.
  Be honest. A run where things broke and you worked around them is more useful than a tidy summary
  that hides it.

## Rules

- Only use my org and the key in `~/.pixeltable/config.toml`. Do not create or use any other org.
- Non-interactive only. No `vercel login`, no editors, no prompts that block. Skip and tell me if a
  step needs interactive input.
- You are a user of the released `pixeltable` 0.7.4. Report bugs, do not patch pixeltable's source.
- Clean up on request: `pxt service prune`, `pxt db stop`, `pxt db delete` (delete is irreversible).
