# Build a Pixeltable Cloud app with your agent

Fill in the brackets and hand this whole file to your coding agent. It builds and deploys a real app
on your cloud database and reports back.

---

You are building a real application on Pixeltable Cloud and deploying it to a hosted database. Read
`AGENTS.md` and `CLOUD_QUICKSTART.md` in this repo and follow the quickstart for every `pxt` command.
Add the API reference: `npx skills add pixeltable/pixeltable-skill`. Any docs page takes a `.md`
suffix for clean reading, e.g. https://docs.pixeltable.com/platform/cli.md.

## Pick the app

| # | App | In → out | The Pixeltable work | Needs |
|---|-----|----------|---------------------|-------|
| 1 | Auto-crop videos | video → 9:16 clip | extract frame → YOLOX detect → GPT picks the product → crop | YOLOX + OpenAI |
| 2 | Search + generate images | image library + a prompt | CLIP embedding index to search by text, plus a computed column that generates a new image | CLIP + image model |
| 3 | Audio intelligence | podcast/call audio → searchable + summarized | Whisper transcript → segments (view) → topics/summary → embedding index | Whisper + OpenAI |

Build: **<app number, or describe your own>**.

## Step 1: set up

- Ask me which environment manager to use (uv, venv, conda, poetry), then follow that option in
  `CLOUD_QUICKSTART.md` section 1. Do not assume.
- Confirm my key: `pxt config` (my `pixeltable.api_key` shows `<redacted>`). Get my org: `pxt org list`.
- My org slug: **<your-org>**. Use it in every `pxt://` URI. Never touch a database you did not create.

## Step 2: build and ship

- Start from `pxt service example --out app.py` and keep the class-based shape (`TableModel` +
  `FastAPIRouter`); rewrite it into the app above. This shape is underdocumented, so do not switch to
  ad-hoc `create_table` scripts.
- Prefer the CLI (`pxt schema`, `pxt service`, `pxt db`) over writing your own tooling.
- Declare the database in `pyproject.toml`, then follow quickstart section 4:
  `pxt db update -f` (first build takes several minutes) → `pxt schema update` → `pxt service update -f`
  → `pxt service list` for the URL → `curl` a route to prove it works.
- If a computed column calls a provider, pass the key both ways the quickstart shows
  (`secrets.* = 'env:VAR'` and `pxt secret set`). Use cheap models (`gpt-4o-mini`).
- Tell me to open `pxt dashboard` (https://docs.pixeltable.com/platform/dashboard.md) to watch the
  tables and computed columns fill in.

## Step 3: iterate

Change `app.py`, then run the reconcile loop: `pxt schema diff` / `pxt service diff` (exit 2 = pending),
then `update`. Dropping a column needs `--allow-destructive`.

## Step 4: report back to me

- What you built: the tables, computed columns, endpoints.
- The live service URL and one `curl` call that works, with its output.
- Anything that errored, surprised you, or contradicted the docs, with the exact command and output.
  Be honest; a run where things broke is more useful than a tidy summary that hides it.

## Rules

- Only my org and the key in `~/.pixeltable/config.toml`. Do not create or use any other org.
- Non-interactive only: `pxt db update` and `pxt service update` prompt, so always pass `-f`. No
  editors, no `login` flows. Skip and tell me if a step needs interactive input.
- You are a user of the released `pixeltable` 0.7.4. Report bugs, do not patch its source.
