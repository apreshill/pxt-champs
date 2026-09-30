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

Follow the phases in `AGENTS.md`. Do phase 2 before phase 3. Stop at the end of the phase you were given.

- Ask me which environment manager to use (uv, venv, conda), then follow that option in the README's Environment section. Do not assume. Ask this in phase 1, before you install anything.
- In phase 3, confirm this machine is signed in with `pxt whoami`. If it says not signed in, stop and ask me to run `pxt login`. Do not run `pxt login` yourself.

## Report back to me

After phase 2, report the local URL from `pxt service list`, the curl with no key, and the rows.

After phase 3, report the cloud URL from `pxt service list`, the hosted rows, and the curl. That curl needs `X-api-key`. If I have not given you a key, show the curl with a placeholder and say the call was not made.

Also report what you built, and anything that errored or contradicted these docs, with the exact command and output.

## Rules

- Only the org from `pxt org list`. Do not create another org.
- No editors. `pxt login`, and the API key for the hosted curl, are the steps that need me. Skip and tell me if any other step needs interactive input.
- You are a user of the released `pixeltable` 0.7.10. Report bugs, do not patch its source.
