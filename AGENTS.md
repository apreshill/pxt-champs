# AGENTS.md

Pixeltable is an OLTP database for multimodal AI. You declare tables and computed columns as a class-based schema and define a service over them in one `app.py`, then create and serve it with the `pxt` CLI.

Do the phases below in order. Finish the phase you were given, then stop. Do not start the next phase until the human asks for it. Do not open an interactive editor.

Add the skill for the schema DSL before you write `app.py`: `npx skills add pixeltable/pixeltable-skill`. The SDK API reference is at https://docs.pixeltable.com/sdk/latest/pixeltable.

The CLI is a `pxt <noun> <verb>` grammar. `schema`, `service`, and `db` share `diff` and `update`. Run `pxt <noun> --help` rather than guessing. Docs: https://docs.pixeltable.com (any page takes a `.md` suffix). A `diff` that exits 2 means there is something to apply. That is the preview, not a failure.

Cloud deploy follows the [Pixeltable Cloud guide](https://github.com/pixeltable/pixeltable/blob/main/docs/release/cloud.mdx).

Use one `app.py`. Use class-based schemas. Prefer built-in UDFs and UDAs over custom functions. You are a user of the released `pixeltable` package. Report bugs. Do not patch its source.

## Phase 1. Plan

Read the spec the human named, and read this file. Propose how you will build the service.

Do not edit files. Do not run `pxt`. Stop after the plan.

## Phase 2. Local

Build and run on this machine only. The target is a local catalog path, `/crop`, not a `pxt://` URI.

1. Install Pixeltable with the environment manager the human chose, using the Environment section of the README, if `pxt --version` is not already 0.7.12 in this project.
2. If `pyproject.toml` has no `[[tool.pixeltable.database]]` entry, run `pxt init`. That entry is the local database. Leave it unnamed.
3. Write `app.py`.
4. `pxt schema diff app.py /crop`
5. `pxt schema update app.py /crop`
6. `pxt service diff app.py /crop`
7. `pxt service update app.py /crop -f`
8. Insert one test input and show the rows with `pxt rows /crop/<table>`.
9. `pxt service list /crop`. Copy the `http://127.0.0.1:<port>` URL from that output. Call one route on it with no API key. Show the command and the response.
10. From the rows and the response, name the video column and show the file path or URL for the cropped video. The human opens that path to watch it.

Do not run `pxt db`. Do not pass a `pxt://` URI to any command. Do not create an API key. Stop and show the local URL, the curl, the rows, and the path or URL of the cropped video.

## Phase 3. Cloud

Start this phase only after the human says the local result is good.

A `pxt login` session is enough to deploy. Check `pxt whoami`. If it says not signed in, stop and ask the human to run `pxt login`. Do not run `pxt login` yourself. Do not create an API key unless the human asks. Do not read or write `~/.pixeltable/config.toml`.

Get the org slug from `pxt org list`. The first word is the slug. `pxt whoami` does not print it.

Two addresses. Do not mix them.

- `DB` is `pxt://<org>:<db>` with no catalog path. `pxt db` accepts only this form.
- `PATH` is `$DB/crop`. `pxt schema` and `pxt service` take `PATH`.

Choose `<db>` like this. Run `pxt ls pxt://<org>:main`. If that catalog has tables, `<db>` is a new name, `crop`, and you do not update `main`. If `main` has no tables, `<db>` is `main`.

Keep the local database entry. Add a second `[[tool.pixeltable.database]]` entry in `pyproject.toml`. Do not put the hosted name on the local entry.

```toml
[[tool.pixeltable.database]]
name = 'pxt://<org>:<db>'
```

Then run these commands, in this order. Pass `-f` on `pxt db update` and `pxt service update`.

1. `pxt db diff $DB`
2. `pxt db update $DB -f`
3. `pxt schema diff app.py $PATH`
4. `pxt schema update app.py $PATH`
5. `pxt service diff app.py $PATH`
6. `pxt service update app.py $PATH -f`
7. `pxt service list $PATH`
8. Insert one test input into the hosted table and show `pxt rows $PATH/<table>`.

`pxt db update` uploads the project and builds the image when the Python environment changed. The first build takes several minutes. It does not insert rows and it does not start HTTP. `pxt schema update` creates the tables. `pxt service update` starts the hosted routes. `pxt service run` is local only. Do not use it in this phase.

Copy the service URL from `pxt service list`. Do not invent the hostname. A call to that URL needs the human's key in the `X-api-key` header. A call with no key returns 401. Ask the human for the key, or ask them to run `pxt key create`. If they have not given you a key, show the curl with a placeholder and say the call was not made.

Stop. Report the local URL, the cloud URL, both curls, the rows, and the path or URL of the cropped video in each place.
