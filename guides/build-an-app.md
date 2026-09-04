# Build an app on cloud-hosted tables with your agent

You are my coding agent. Build an application on my hosted Pixeltable database and deploy it. Read
`AGENTS.md` in this repo and follow it for every `pxt` command. Add the Pixeltable skill for the schema
DSL: `npx skills add pixeltable/pixeltable-skill`. The SDK API reference is at
https://docs.pixeltable.com/sdk/latest/pixeltable.

## Pick what to build

Ask me which:

- **The autocropper** — a worked example, fully specified below.
- **My own app** — ask me to describe it, then build that instead. Everything below except the
  autocropper spec still applies.

### The autocropper

The autocropper reframes a video to a target aspect ratio by finding a product in it and cropping
around that. Three inputs — the source **video**, a free-text **product** description, and the target
**width/height ratio** (e.g. `0.5625` for 9:16 vertical) — run through five stages:

1. **Frame.** Take one representative frame, the first at t=0.
2. **Detect.** Run a general-purpose object detector (e.g. YOLOX) over that frame, producing candidate
   boxes with class labels and confidence scores; collapse the distinct labels into a candidate class
   list.
3. **Match.** Ask an LLM which detected class best matches the product description, constrained to emit
   a single class name from that list, or `none`.
4. **Locate and size.** Resolve the chosen class to one box — the highest-confidence detection with that
   label — then derive a fixed crop window: center on the box's midpoint, grow whichever dimension is
   deficient until it hits the target ratio, shrink it if it exceeds the frame, and translate it to stay
   fully inside the frame.
5. **Reframe.** Apply that one static window to every frame of the video, producing the reframed video.

Model each stage as a computed column on one table, so inserting a row runs the whole chain and any
stage can be inspected on its own. Stage 4's geometry is pure arithmetic — a `@pxt.udf`; stage 5 is a
video transform — a Pixeltable video function or a `@pxt.udf`.

## Step 1: set up

- Ask me which environment manager to use (uv, venv, conda, poetry), then follow that option in the
  README's Environment section. Do not assume.
- Confirm my Pixeltable API key with `pxt config` (`pixeltable.api_key` shows `<redacted>`), and get my
  org slug from `pxt org list`. Use that slug in every `pxt://` URI, and never touch a database you did
  not create.

## Step 2: build and ship

- Start from `pxt service example --out app.py` and keep the class-based shape (`TableModel` +
  `FastAPIRouter`); rewrite it into the app. Do not switch to ad-hoc `create_table` scripts.
- Model the work as computed columns on a table, and serve it with a `FastAPIRouter` route.
- Declare the database in `pyproject.toml`, then follow AGENTS.md's deploy loop: `pxt db update -f`
  (first build takes several minutes) → `pxt schema update` → `pxt service update -f` → `pxt service
  list` for the URL → `curl` a route to prove it works.
- If a computed column calls a provider (an LLM, a detector), pass the key both ways AGENTS.md shows
  (`secrets.* = 'env:VAR'` and `pxt secret set`). Use cheap models.
- Tell me to open `pxt dashboard` to inspect the tables and computed columns.

## Step 3: iterate

Change `app.py`, then run the reconcile loop: `pxt schema diff` / `pxt service diff` (exit 2 = pending),
then `update`. Adding a column is safe; you cannot alter one in place (drop it with `--allow-destructive`
and add it back).

## Step 4: report back to me

- What you built: the tables, computed columns, endpoints.
- The live service URL and one `curl` call that works, with its output.
- Anything that errored, surprised you, or contradicted the docs, with the exact command and output.
  Be honest; a run where things broke is more useful than a tidy summary that hides it.

## Rules

- Only my org and the key in `~/.pixeltable/config.toml`. Do not create or use any other org.
- Non-interactive only: `pxt db update` and `pxt service update` prompt, so always pass `-f`. No
  editors, no `login` flows. Skip and tell me if a step needs interactive input.
- You are a user of the released `pixeltable` 0.7.5. Report bugs, do not patch its source.
