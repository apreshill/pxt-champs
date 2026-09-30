# Quickstart

You send a title. You get back the title in capitals, a short summary, and an id the database generated.

```json
{"id": "<generated>", "title_upper": "HELLO", "summary": "hello"}
```

You get that response on your machine first. That call needs no account and no API key. After you have seen it, the same `app.py` goes to a hosted database. A `pxt login` session is enough for that deploy. You do not need an API key until the last step, when you call the hosted URL. The first image build takes several minutes.

This follows the [Pixeltable Cloud guide](https://github.com/pixeltable/pixeltable/blob/main/docs/release/cloud.mdx). It assumes you finished the README install and this shell has `source .venv/bin/activate`. A new shell needs that `source` again.

Commands you run in the shell are in `bash` blocks. Where a command shows `<your-org>`, use the first word from `pxt org list`. Where it shows `<port>`, use the port from `pxt service list`.

`pxt schema diff` and `pxt db diff` exit 2 when there is something to apply. That exit code is the preview.

## 1. Write the app

One file holds the table and the HTTP routes. `title` is the value you send. `title_upper` is the title in capitals. `summary` is the start of the title. A function in the file named `excerpt` computes `summary`.

```bash
pxt init
pxt service example --out app.py
```

This repo has a `pyproject.toml`, so `pxt init` appends a database entry there and leaves the dependencies in place. It prints `wrote pyproject.toml`. That entry is the local database. Leave it unnamed.

## 2. See the response on your machine

`/hello` is a directory in your local catalog. If you already have one with that name, pick another word and use it in place of `hello` below.

```bash
pxt schema diff   app.py /hello
pxt schema update app.py /hello
pxt service update app.py /hello -f
pxt service list  /hello
```

`schema diff` exits 2. `schema update` creates `hello/docs`. `service update` starts the service on this machine. `-f` skips the confirmation prompt.

`service list` prints a line like `http://127.0.0.1:<port>`. Copy that URL and add `/docs`. This call has no key.

```bash
curl -sS -X POST http://127.0.0.1:<port>/docs \
  -H 'Content-Type: application/json' \
  -d '{"title": "hello", "body": null}'
```

The response is the JSON at the top of this guide. `id` is a key the database generated. You did not send it.

Read the row back:

```bash
pxt rows /hello/docs
```

You can stop here. You have seen what happens when you send a title. The rest puts this same `app.py` on a hosted database.

## 3. Sign in

A login session is enough for the deploy. You do not need an API key yet.

Follow the Sign in section in the README. Then confirm:

```bash
pxt whoami
pxt org list
```

The org slug is the first word of `pxt org list`. If you have no organization, create one. The name you pass is the slug, and the command also creates your first database, `main`.

```bash
pxt org create <your-org>
```

If `pxt whoami` says the commands use an API key from the config file or from `PIXELTABLE_API_KEY`, that key is used instead of the login session. You can still deploy.

## 4. Add the hosted database

Keep the local entry from `pxt init`. Add a second entry for the hosted database. In this repo the section name is `tool.pixeltable.database`.

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:main'
```

`main` is the database from `pxt org create`. The commands below use that name.

## 5. Upload the project

`pxt db update` uploads this project onto `main` and updates its image. It does not insert a row, and it does not start HTTP.

The image is the Python environment. That is your dependencies, the Python version, and any system packages. The first build takes several minutes. The command prints a plan, then waits, then prints `applied`. A later edit to `app.py` is an upload. It does not rebuild the image, unless a dependency, the Python version, or a system package changed.

```bash
pxt db diff   pxt://<your-org>:main
pxt db update pxt://<your-org>:main
```

`db diff` exits 2 when there is something to apply. `db update` asks you to confirm.

Confirm the database before you continue.

```bash
pxt db status pxt://<your-org>:main
```

Go on when the first line shows the name and `AVAILABLE`. A later line may still say the project upload is pending. You can create the table while that line is pending.

## 6. Create the table and start HTTP

`pxt schema update` creates the table. It does not start HTTP. `pxt service update` starts the hosted routes. `pxt service run` only starts routes in your local terminal, so the cloud command is `pxt service update`.

```bash
pxt schema update app.py pxt://<your-org>:main
pxt service update app.py pxt://<your-org>:main
pxt service list  pxt://<your-org>:main
```

`service list` prints the service URL and its routes. Copy that URL. It looks like `https://<your-org>-main.svc.pxt.run/ingest`. The insert route is `/docs` on that URL.

## 7. Insert a row

The login session is enough for this. Save it as `insert.py`, set `<your-org>`, and run it. You do not pass `id`.

```python
import pixeltable as pxt

docs = pxt.get_table('pxt://<your-org>:main/docs')
docs.insert(title='Hello', body='world')
print(docs.select(docs.title, docs.title_upper).collect())
```

```bash
python insert.py
```

The result includes `Hello` and `HELLO`. You can also insert from the [Cloud dashboard](https://www.pixeltable.com/dashboard).

## 8. Call the hosted service

An API key is for this call. It is also what a backend or a CI job uses. Keep the key out of browser code. If a web page needs the service, the page calls your backend, and the backend sends the key.

If you do not have a key yet, create one. The command prints the secret once. `pxt key list` shows the name and cannot show the secret again. A key created without `--grant` acts as you.

```bash
pxt key create my-app
```

Copy the service URL from `pxt service list`. Send the key in `X-api-key`.

```bash
export PIXELTABLE_API_KEY='your-key'
SERVICE_URL='URL from pxt service list'
curl -X POST "$SERVICE_URL/docs" \
  -H "X-api-key: $PIXELTABLE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"title": "Hello from HTTP", "body": "world"}'
```

A call with no key returns 401. The response has the same fields as the local call. `title_upper` is `HELLO`. `summary` is the start of the title, from `excerpt`. `id` is generated.

To build a real application with your coding agent, see `build-an-app.md`.
