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

- Ask me which environment manager to use (uv, venv, conda), then follow that option in the
  README's Environment section. Do not assume.
- Confirm this machine is signed in with `pxt whoami`. If it says not signed in, stop and ask me to run
  `pxt login` (a browser confirmation). Do not run `pxt login` yourself. A login session is enough to deploy. Do not create an API key unless I ask.
- Get my org slug from `pxt org list`. The first word is the slug. `pxt whoami` does not print it. Use that slug in every `pxt://` URI.
- Keep the local database entry from `pxt init`. Add a second `[[tool.pixeltable.database]]` entry for the hosted database. Do not put the hosted name on the local entry.
- Use `pxt://<org>:main` when `main` is the empty database from `pxt org create`. If `main` already has another project, use a new database name. Never run `pxt db update` against a database you did not create for this app.

## Report back to me

- What you built: the tables, computed columns, endpoints.
- The local URL and the cloud URL from `pxt service list`. The local curl needs no key. The cloud curl needs `X-api-key`. Ask me for that key, or ask me to run `pxt key create`. If I have not given you a key, show the curl with a placeholder and say the call was not made. Do not invent a hostname.
- Anything that errored, surprised you, or contradicted the docs, with the exact command and output.
  Be honest; a run where things broke is more useful than a tidy summary that hides it.

## Rules

- Only the org from `pxt org list`. Do not create another org, and do not read or write
  `~/.pixeltable/config.toml`.
- Order on a hosted target is `pxt db update`, then `pxt schema update`, then `pxt service update`. `pxt service run` is local only.
- Non-interactive after sign-in: `pxt service update` and `pxt db update` prompt, so always pass `-f`.
  No editors. `pxt login` is the one step that needs me, unless I still need to create or paste an API key for the hosted curl. Skip and tell me if any other step needs interactive input.
- You are a user of the released `pixeltable` 0.7.10. Report bugs, do not patch its source.
