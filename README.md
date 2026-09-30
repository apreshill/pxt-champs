# pxt-champs

Pixeltable is a database for AI apps. Your media, the model outputs you derive from that media, and your app's state live in one database. You declare a schema, insert data, and query it. The database stores that data and runs the models and transforms that fill the computed columns.

This repo is a beta test of hosted tables. A hosted table is that same database on Pixeltable's infrastructure. You address it with a URI like `pxt://<your-org>:<db>`.

## What you are building

You send a title. You get back the title in capitals, a short summary, and an id the database generated.

```json
{"id": "<generated>", "title_upper": "HELLO", "summary": "hello"}
```

You see that response on your own machine first. That call needs no account and no API key. The quickstart then deploys the same app. A `pxt login` session is enough for that deploy. You do not need an API key until you call the hosted URL over HTTP. The first image build takes several minutes.

## Environment

You need Python 3.11 or newer, and `pixeltable[serve]` 0.7.12. This repo pins that version. The install is about 500MB, so do it before you start the guide.

For the quickstart, install [uv](https://docs.astral.sh/uv/), then clone this repo:

```bash
git clone https://github.com/apreshill/pxt-champs && cd pxt-champs
uv sync
source .venv/bin/activate
```

That activates this project's environment in the current shell, so `pxt` and `python` are the ones just installed. A new shell needs `source .venv/bin/activate` again.

For your own app, start a fresh project. Any manager in the table works. `pixeltable` has to be a dependency. The project needs a lockfile at its root, because `pxt db update` builds the hosted image from that file.


| manager          | commands                                                                                                                       | lockfile           |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------ |
| uv (recommended) | `uv init --bare && uv add 'pixeltable[serve]' && source .venv/bin/activate`                                                    | `uv.lock`          |
| venv + pip       | `python3 -m venv .venv && source .venv/bin/activate && pip install 'pixeltable[serve]' && pip freeze > requirements.txt`       | `requirements.txt` |
| conda            | `conda create -n app python=3.12 -y && conda activate app && pip install 'pixeltable[serve]' && pip freeze > requirements.txt` | `requirements.txt` |


Make sure `pxt` resolves to the one you installed (`which pxt`). Another venv or conda base on PATH can shadow it. Confirm the version.

```bash
pxt --version    # pxt 0.7.12
```

## Sign in

Do this when the quickstart tells you to deploy. The first half of the quickstart runs on your machine and does not need an account.

`pxt login` signs this machine in to Pixeltable Cloud. It prints a code and opens a browser, where you confirm that code.

```bash
pxt login
pxt whoami
pxt org list
```

`pxt org list` prints your org slug as the first word. You use that word in every `pxt://` URI. `pxt whoami` does not print the slug.

If `pxt login` says there is no organization yet, create one. The name you pass is that org slug. This also creates your first database, `main`.

```bash
pxt org create <your-org>
```

The session stays on this machine, and later commands renew it. `pxt logout` forgets it. That session is enough to deploy. An API key in `~/.pixeltable/config.toml` or in `PIXELTABLE_API_KEY` is used instead of the session when one is set. The environment variable wins. If `pxt whoami` says the commands use that key, you are signed in that way.

Create an API key only when a program calls the hosted URL. The quickstart does that last. The header on that call is `X-api-key`.

## Pick your path

- **Try it yourself.** `guides/quickstart.md` gets the response above from your machine, then deploys the same app to `main`. You do not need a model provider key.
- **Build a real app with your coding agent.** `guides/build-an-app.md` is a video autocropper, or your own app. Do the quickstart first. Your agent does the work. You call a URL on your machine, open the cropped video from that response, and play the same video in the dashboard. Then you deploy that app.

## Links

Docs [https://docs.pixeltable.com](https://docs.pixeltable.com) · Dashboard [https://docs.pixeltable.com/platform/dashboard.md](https://docs.pixeltable.com/platform/dashboard.md)
