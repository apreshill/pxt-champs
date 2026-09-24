# Quickstart: build and serve a cloud-hosted table

Cloud-hosted tables run a Pixeltable database on hosted infrastructure, addressed by a `pxt://` URI
instead of a local path. In this quickstart you create one, declare a table, insert a row the database
computes a column from, and serve the table over HTTP. No agent, no provider API keys, no model
downloads.

This assumes you finished the README setup: this repo cloned, dependencies installed, and your
Pixeltable API key set (in `~/.pixeltable/config.toml` or the `PIXELTABLE_API_KEY` environment
variable).

The commands below assume the environment from the README setup is active (`source .venv/bin/activate`
for this repo). Then `pxt` and `python` are the ones that project installed. A new shell needs that
`source` again.

Two kinds of code appear below:

1. **CLI commands** run in your shell as `pxt <noun> <verb>` (like `pxt schema update`), in `bash` blocks.
2. **SDK code** is Python in a `.py` file, `pxt.<call>(...)` (like `pxt.get_table(...)`), in `python` blocks.

One name is yours to fill in — `<your-org>`, your org slug. The rest are example names.

Check your key, and note your org slug (you use it below):

```bash
pxt config      # pixeltable.api_key shows <redacted>
pxt org list    # the first word is your org slug; you put it in the database name in step 2
```

## Terms

**The address.** A cloud table is addressed by a URI:

```
pxt://<org>[:<db>][/<path>][:<version>]
```

| part | required | what it names |
|------|----------|---------------|
| `<org>` | yes | your org slug, from `pxt org list` |
| `<db>` | no | a database you name. Without it, `pxt://<org>` names the org (`pxt org status`). `pxt db list` prints every database your key reaches, and it takes no URI. |
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
pxt schema example                            # print a full example to read
pxt schema example --brief --out schema.py    # --brief: minimal; --out: write to schema.py
```

Open `schema.py`:

```python
class Docs(TableModel, name='docs'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)  # a generated primary key
    title: pxt.String                         # a stored column
    body: pxt.String | None                   # a stored column that may be null
    title_upper = pxtf.string.upper(title)    # a computed column: an assignment, not an annotation


class Titled(TableModel, name='titled', base=Docs.where(Docs.title != '')):
    headline = Docs.title_upper + '!'         # a view of Docs, filtered by its base= query
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
pxt init
```

Open pyproject.toml. `pxt init` appended an entry with no name, which is the local database. Add a
`name` line so that entry is your hosted database. Use your org slug and a database name you pick:

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:champs'
```

## 3. Create the database

This creates the database and builds its hosted image from your project's lockfile — it installs your
dependencies into the image, so the first build takes several minutes.

```bash
pxt db diff   pxt://<your-org>:champs       # read-only: shows the create plan
pxt db update pxt://<your-org>:champs -f    # applies it; -f skips the confirmation prompt
```

`db diff` exits 2 when there is something to apply. That is the preview, not a failure. The first time, the plan
says the database will be created, the image will be rebuilt, and the project will be uploaded:

```
+ pxt://<your-org>:champs      will be created  absent
    the image will be rebuilt from the project environment  [additive]
    the project will be uploaded  [additive]

Plan: 2 change(s), 0 destructive
```

`db update` does that work. The image rebuild is the slow part, and the first one takes several minutes.
Later updates upload changed files without a rebuild, unless a dependency, the Python version, or a system
package changed.

Confirm the database is live. The first line shows the name and `AVAILABLE`:

```bash
pxt db status pxt://<your-org>:champs
```

## 4. Create the tables

```bash
pxt schema diff   schema.py pxt://<your-org>:champs    # read-only: what update will create
pxt schema update schema.py pxt://<your-org>:champs    # creates the tables
```

`schema update` prints:

```
created   pxt://<your-org>:champs/docs
created   pxt://<your-org>:champs/titled
```

Confirm the tables and their columns:

```bash
pxt ls --tree pxt://<your-org>:champs
pxt describe   pxt://<your-org>:champs/docs
```

## 5. Insert a row

The CLI reconciles and inspects tables, but it cannot write rows. That is the SDK's job. Save this as
`insert.py`, set `<your-org>`, and run it. You do not pass `id`. The database generates it, computes
`title_upper`, and stores both.

```python
import pixeltable as pxt

docs = pxt.get_table('pxt://<your-org>:champs/docs')   # set <your-org>
docs.insert([{'title': 'hello world', 'body': 'a first doc'}])
print(docs.select(docs.title, docs.title_upper).collect())
```

```bash
python insert.py
```

It prints the row with the computed `title_upper='HELLO WORLD'`. Or read the rows from the CLI:

```bash
pxt rows pxt://<your-org>:champs/docs
```

## 6. Browse the table

Open the dashboard to browse the table and its computed column.

```bash
pxt dashboard
```

## 7. Serve a table as an API

A **service** turns a table into an HTTP API: routes clients call to insert or query it over the
network, without the SDK. `pxt service example` writes an app.py with a table plus a service:

```bash
pxt service example --out app.py    # a table and an `ingest` service
```

app.py declares its own table, also named `docs`, which collides with the `docs` you built in steps
1–4. Rename it: in app.py, change `name='docs'` to `name='submissions'`. The service is named `ingest`,
with three routes over `submissions`:

- `POST /docs` inserts a row from `title` and `body`, and returns the generated `id` plus `title_upper` and `summary`.
- `POST /docs/update` matches a row by `id` and rewrites `title`.
- `POST /titles` returns `title_upper` for a title without storing a row.

`app.py` defines its own function, `excerpt`, and the hosted database runs that function from the
project files. Upload them before you create the table. This does not rebuild the image, because the
dependencies did not change.

```bash
pxt db update     pxt://<your-org>:champs -f
pxt schema update app.py pxt://<your-org>:champs
pxt service update app.py pxt://<your-org>:champs -f    # -f skips the confirmation prompt
pxt service list  pxt://<your-org>:champs               # prints the service URL and routes
```

Copy the `POST /docs` URL from that output and call it. The host is `https://<your-org>-champs.svc.pxt.run`
and the insert path is `/ingest/docs`:

```bash
curl -X POST https://<your-org>-champs.svc.pxt.run/ingest/docs \
  -H 'Content-Type: application/json' -d '{"title": "hello", "body": null}'
```

The response is the route's outputs, filled in by the database:

```json
{"id": "<generated>", "title_upper": "HELLO", "summary": "hello"}
```

From one schema, the same computed columns reach you three ways: the SDK, the CLI, and now this API.

To build a real application with your coding agent, see `build-an-app.md`.
