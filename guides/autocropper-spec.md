# Autocropper spec

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


## Set up

- Ask me which environment manager to use (uv, venv, conda, poetry), then follow that option in the
  README's Environment section. Do not assume.
- Confirm my Pixeltable API key with `pxt config` (`pixeltable.api_key` shows `<redacted>`), and get my
  org slug from `pxt org list`. Use that slug in every `pxt://` URI, and never touch a database you did
  not create.

## Report back to me

- What you built: the tables, computed columns, endpoints.
- The local URL and the cloud URL, each with one working `curl` call and its output.
- Anything that errored, surprised you, or contradicted the docs, with the exact command and output.
  Be honest; a run where things broke is more useful than a tidy summary that hides it.

## Rules

- Only my org and the key in `~/.pixeltable/config.toml`. Do not create or use any other org.
- Non-interactive only: `pxt service update` and `pxt db update` prompt, so always pass `-f`. No editors,
  no `login` flows. Skip and tell me if a step needs interactive input.
- You are a user of the released `pixeltable` 0.7.5. Report bugs, do not patch its source.
