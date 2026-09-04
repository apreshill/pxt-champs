# Quickstart: build and serve a cloud-hosted table

Cloud-hosted tables run a Pixeltable database on hosted infrastructure, addressed by a `pxt://` URI
instead of a local path. In this quickstart you create one, declare a table, insert a row the database
computes a column from, and serve the table over HTTP. No agent, no provider API keys, no model
downloads.

This assumes you finished the README setup: this repo cloned, dependencies installed, and your
Pixeltable API key set (in `~/.pixeltable/config.toml` or the `PIXELTABLE_API_KEY` environment
variable).

The commands below use `uv run`, which runs a command in this project's virtual environment without
activating a shell first. On another environment manager, activate your environment and drop the
`uv run`.

Two kinds of code appear below:

1. **CLI commands** run in your shell as `pxt <noun> <verb>` (like `pxt schema update`), in `bash` blocks.
2. **SDK code** is Python in a `.py` file, `pxt.<call>(...)` (like `pxt.get_table(...)`), in `python` blocks.

One name is yours to fill in — `<your-org>`, your org slug. The rest are example names.

Check your key, and note your org slug (you use it below):

```bash
uv run pxt config      # pixeltable.api_key shows <redacted>
uv run pxt org list    # prints your org slug; you put it in the database name in step 2
```

## Terms

**The address.** A cloud table is addressed by a URI:

```
pxt://<org>[:<db>][/<path>][:<version>]
```

| part | required | what it names |
|------|----------|---------------|
| `<org>` | yes | your org slug, from `pxt org list` |
| `<db>` | no | a database you name. Without it, `pxt://<org>` names the org (`pxt db list pxt://<org>`). |
| `<path>` | no | a table or view in the catalog, nesting like `kb/docs`. Without it, `pxt://<org>:<db>` names the catalog root. |
| `<version>` | no | a table's version, bumped on every write. Append `:<n>` to read version n; without it, the latest. |

**What a database holds.** A database's contents are its catalog. From largest to smallest:

- **database** — a Pixeltable database. A cloud-hosted one runs on hosted infrastructure at `pxt://<org>:<db>`.
- **catalog** — the tables, views, and directories in a database. `pxt ls --tree` prints it.
- **directory** — a namespace in the catalog that groups tables and views under a path prefix, not a
  filesystem directory. `kb/docs` is the table `docs` under namespace `kb`.
- **table** — rows of typed columns; some are mutable (you insert them), others the database computes
  from the schema.
- **view** — a table derived from a base table: a query over it, or an iterator that expands each row
  into many (a video into frames, a document into chunks). The database keeps it current.

## 1. Write the schema

A schema is a file that declares your tables and their columns: some are mutable (you insert them),
others the database computes from the schema. The example command writes a starter one:

```bash
uv run pxt schema example                            # print a full example to read
uv run pxt schema example --brief --out schema.py    # --brief: minimal; --out: write to schema.py
```

Open `schema.py`:

```python
class Docs(TableModel, name='docs'):
    title: pxt.String
    body: pxt.String | None
    title_upper = pxtf.string.upper(title)              # computed from title

class Titled(TableModel, name='titled', base=Docs.where(Docs.title != '')):
    headline = Docs.title_upper + '!'                   # a view of docs
```

A table's address has three parts, each from a different place:

| part | from | in this example |
|------|------|-----------------|
| `<org>` | `pxt org list` | your org slug |
| `<db>` | you name it in step 2 | `champs` |
| `<path>` | each class's `name=` above | `docs`, and `titled` (the view) |

So the docs table is at `pxt://<your-org>:champs/docs`. You reuse these paths in every later command.

## 2. Declare the hosted database

`pxt init` marks this directory as a Pixeltable project. This repo has a pyproject.toml, so it adds
the database entry there, under `[[tool.pixeltable.database]]`. (With no pyproject.toml it writes a
standalone `pixeltable.toml` instead.)

```bash
uv run pxt init
```

Open pyproject.toml and set that entry's `name` to your org slug (from step 1) and a database name
you pick:

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:champs'
```

## 3. Create the database

This creates the database and builds its hosted image from your project's lockfile — it installs your
dependencies into the image, so the first build takes several minutes.

```bash
uv run pxt db diff   pxt://<your-org>:champs       # read-only: shows the create plan
uv run pxt db update pxt://<your-org>:champs -f    # applies it; -f skips the confirmation prompt
```

It ends with:

```
= pxt://<your-org>:champs   applied  AVAILABLE
```

Confirm the database is live:

```bash
uv run pxt db status pxt://<your-org>:champs
uv run pxt db status pxt://<your-org>:champs --json    # --json: "state": "AVAILABLE"
```

## 4. Create the tables

```bash
uv run pxt schema diff   schema.py pxt://<your-org>:champs    # read-only: what update will create
uv run pxt schema update schema.py pxt://<your-org>:champs    # creates the tables
```

`schema update` prints:

```
created   pxt://<your-org>:champs/docs
created   pxt://<your-org>:champs/titled
```

Confirm the tables and their columns:

```bash
uv run pxt ls --tree pxt://<your-org>:champs
uv run pxt describe   pxt://<your-org>:champs/docs
```

## 5. Insert a row

The CLI reconciles and inspects tables, but it cannot write rows — that is the SDK's job. Save this as
`insert.py`, set `<your-org>`, and run it. The database computes `title_upper` and stores it.

```python
import pixeltable as pxt

docs = pxt.get_table('pxt://<your-org>:champs/docs')   # set <your-org>
docs.insert([{'title': 'hello world', 'body': 'a first doc'}])
print(docs.select(docs.title, docs.title_upper).collect())
```

```bash
uv run python insert.py
```

It prints the row with the computed `title_upper='HELLO WORLD'`. Or read the rows from the CLI:

```bash
uv run pxt rows pxt://<your-org>:champs/docs
```

## 6. Browse the table

Open the dashboard to browse the table and its computed column.

```bash
uv run pxt dashboard
```

## 7. Serve a table as an API

A **service** turns a table into an HTTP API: routes clients call to insert or query it over the
network, without the SDK. `pxt service example` writes an app.py with a table plus a service:

```bash
uv run pxt service example --out app.py    # a table and an `ingest` service
```

app.py declares its own table, also named `docs`, which collides with the `docs` you built in steps
1–4. Rename it: in app.py, change `name='docs'` to `name='submissions'`. The service is named `ingest`,
with two routes over `submissions`: `POST /docs` inserts a row and returns its computed columns, and
`POST /titles` returns the computed columns for a title without storing a row.

Apply the schema, then start the service:

```bash
uv run pxt schema  update app.py pxt://<your-org>:champs
uv run pxt service update app.py pxt://<your-org>:champs -f    # -f skips the confirmation prompt
uv run pxt service list  pxt://<your-org>:champs               # prints the service URL and routes
```

Copy the `POST /docs` URL from that output and call it:

```bash
curl -X POST https://<your-org>-champs.svc.pxt.run/ingest/docs \
  -H 'Content-Type: application/json' -d '{"doc_id": 1, "title": "hello", "body": null}'
```

The response is the row you inserted, with the computed columns filled in by the database and returned
over HTTP. From one schema, the same computed columns reach you three ways: the SDK, the CLI, and now
this API.

To build a real application, hand `build-an-app.md` to your coding agent.
