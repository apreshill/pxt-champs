# Build a video autocropper on cloud-hosted tables

You are my coding agent. Build the app described below on my hosted Pixeltable database and deploy it.
Read `AGENTS.md` and `CLOUD_QUICKSTART.md` in this repo and follow the quickstart for every `pxt`
command. Add the Pixeltable skill (`npx skills add pixeltable/pixeltable-skill`); the SDK API reference
is at https://docs.pixeltable.com/sdk/latest/pixeltable.

## What it does

The autocropper reframes a video to a target aspect ratio by finding a product in it and cropping
around that. It takes three inputs — the source **video**, a free-text **product** description, and the
target **width/height ratio** (e.g. `0.5625` for 9:16 vertical) — and runs five stages:

1. **Frame.** Take one representative frame, the first at t=0.
2. **Detect.** Run a general-purpose object detector (e.g. YOLOX) over that frame, producing candidate
   boxes with class labels and confidence scores; collapse the distinct labels into a candidate class
   list.
3. **Match.** Ask an LLM which detected class best matches the product description, constrained to emit
   a single class name from that list, or `none`.
4. **Locate and size.** Resolve the chosen class to one box — the highest-confidence detection carrying
   that label — then derive a fixed crop window from it: center on the box's midpoint, grow whichever
   dimension is deficient until the window hits the target ratio, shrink it if it exceeds the frame, and
   translate it so it stays fully inside the frame.
5. **Reframe.** Apply that one static window to every frame of the source video, producing the reframed
   video.

## How to build it

Model it as one table where each stage is a computed column, so inserting a row runs the whole chain
and any stage can be inspected or overridden on its own.

- One `TableModel` table. Input columns: `video: pxt.Video`, `product: pxt.String`,
  `target_ratio: pxt.Float`.
- One computed column per stage: the frame, the detections, the candidate class list, the chosen class
  (an LLM call), the resolved box, the crop window, and the reframed video.
- Stage 4's geometry is pure arithmetic — write it as a `@pxt.udf`. Stage 5 is a video transform; use a
  Pixeltable video function or a `@pxt.udf`.
- Serve it with a `FastAPIRouter`: one insert route taking `video`, `product`, and `target_ratio` and
  returning the reframed video. Expose the chosen class and the box too, so a caller can inspect the
  decision.

Keep the class-based shape (`TableModel` + `FastAPIRouter`); do not fall back to ad-hoc `create_table`
scripts. Deploy with the quickstart's reconcile loop: `pxt db update -f` → `pxt schema update` →
`pxt service update -f` → `pxt service list` for the URL → `curl` a route to prove it works.

## Setup and rules

- Ask me which environment manager to use (uv, venv, conda, poetry). Confirm my Pixeltable API key with
  `pxt config` and get my org slug from `pxt org list`. Use my org in every `pxt://` URI; never touch a
  database you did not create.
- The detector and the LLM need provider keys. Pass each both ways the quickstart shows
  (`secrets.* = 'env:VAR'` in the config, and `pxt secret set`), and use cheap models.
- Non-interactive only: `pxt db update` and `pxt service update` prompt, so always pass `-f`.
- Report back: the tables and computed columns you built, the live service URL with one working `curl`
  and its output, and anything that errored or surprised you, with the exact command and output.
