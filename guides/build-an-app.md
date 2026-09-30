# Build a real app with your coding agent

You are working toward a URL. You send a video and a product name. You get the video back, cropped around that product. Your agent writes the app and runs it, first on your machine, then as that URL. It is the same app both times. Only the target changes, from a local name to a `pxt://` URI. Your job is to say what to build, then check the agent's work at each step.

## 1. Choose an app to build

Your agent will need an app spec. You can use one we already wrote with one of our design partners, or
supply your own.

- **The autocropper** — insert a video and a product name, and the app returns the video reframed to a
  target shape (say 9:16 for vertical), cropped around that product. Its full spec is in
  `spec/autocropper-spec.md`.
- **Your own app** — anything that turns media into something useful: search a library of images by
  description, transcribe and summarize calls, pull structured fields out of documents, generate images
  from prompts.

## 2. Hand the spec to your agent

Sign in first, if you have not already (`pxt login` in the README). The agent checks `pxt whoami` and
will not open the browser for you.

To build the autocropper, give your agent this prompt to start:

```
Take a look at spec/autocropper-spec.md

Propose a plan for how to create a service with Pixeltable for this.

Rules: Use the Pixeltable CLI. Use class-based schemas. Write to a single `app.py` file. Always prefer
built-in UDFs and UDAs over custom.

Read `AGENTS.md` in this repo and follow it for every `pxt` command.

A `pxt login` session is enough to deploy. Do not create an API key unless I ask. A hosted HTTP call needs that key in the `X-api-key` header. Ask me before that call. Do not read or write `~/.pixeltable/config.toml`.

Keep the local database entry from `pxt init`. Add a second `[[tool.pixeltable.database]]` entry for the hosted database. Do not put the hosted name on the local entry. Use `pxt://<org>:main` when `main` is the empty database from `pxt org create`. If `main` already has another project, use a new database name and do not update `main`.

Order is `pxt db update`, then `pxt schema update`, then `pxt service update`. Pass `-f` on `pxt db update` and `pxt service update`. Do not use `pxt service run` for a `pxt://` target. Copy the service URL from `pxt service list`. Do not invent the hostname.

Add the Pixeltable skill for the schema DSL: `npx skills add pixeltable/pixeltable-skill`.
```

## 3. Build the app

Review the plan. If it suits you, tell your agent to go ahead:

```
Now create the tables and try it with a test video.
```

Your agent writes an `app.py` — one file holding a class-based schema (a `jobs` table with a computed
column per pipeline stage) and a `FastAPIRouter` with insert, update, and query routes over it. It then
runs the CLI to create the tables and start the service against a **local** target (a path like
`/dicer`, not a `pxt://` URI). Local runs need no image build, so this is instant. When it finishes,
check its work.

## 4. Run it on your machine

All local, no cloud, no build. Look at what the agent wrote:

```bash
cat app.py
```

Apply the schema — the `schema` verbs touch only the tables:

```bash
pxt schema diff   app.py /dicer       # preview the tables
pxt schema update app.py /dicer       # create them
pxt ls /dicer                         # they're there
```

Then start the service — the `service` verbs touch only the routes over those tables:

```bash
pxt service diff   app.py /dicer      # preview the routes; exit 2 means it would start the service
pxt service update app.py /dicer -f   # start the service
```

You now have local endpoints. `pxt service list /dicer` prints the URL. A call to that URL needs no key. Try a route from that list, or post a video and get the reframed result back. Fix anything here, locally, before the cloud.

## 5. Deploy the same app to the cloud

Same `app.py`. A `pxt login` session is enough for this deploy. You do not need an API key until you call the hosted URL.

Keep the local database entry from `pxt init`. Add a second entry. This repo uses `pyproject.toml`, so the section name is `tool.pixeltable.database`.

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:main'
```

`main` is the database `pxt org create` made. If `main` already has another project, such as the quickstart, use a new name instead, for example `pxt://<your-org>:dicer`. Do not update `main` in that case. `pxt db update` creates a database that does not exist yet. On `main`, it uploads this project onto the database that is already there.

The commands split across two addresses. `pxt db` takes the database URI, `pxt://<org>:<db>`, and it rejects a URI that also has a catalog path. `pxt schema` and `pxt service` take that path, which is the database URI plus a directory you pick, such as `/dicer`.

`pxt db update` uploads the project files and rebuilds the image only when the Python environment changed. The environment is the lockfile, the Python version, and any system packages. The first image build takes several minutes. A later edit to `app.py` is an upload, and it does not rebuild the image. The upload has to happen before `schema update`. The hosted database runs your functions from those files. If you skip the upload, `service diff` says the database has to change first and names `pxt db update` as the next command.

```bash
DB=pxt://<your-org>:main                 # or pxt://<your-org>:dicer if main is already in use
PATH=$DB/dicer                           # a catalog directory you pick

pxt db diff   $DB                        # preview; exit 2 means there is something to apply
pxt db update $DB -f                     # upload, and build the image if the environment changed

pxt schema diff   app.py $PATH           # same preview as local, cloud target
pxt schema update app.py $PATH           # create the tables. This does not start HTTP.

pxt ls       $PATH                       # the tables are there
pxt cd       $PATH                       # make that directory your working location
pxt describe jobs                        # inspect a table (relative path, after cd)
```

`pxt service update` starts the hosted routes. `pxt service run` only starts routes in your local terminal.

```bash
pxt service diff   app.py $PATH          # preview; exit 2 means it would start the service
pxt service update app.py $PATH -f
pxt service list   $PATH                 # prints the service URL. Copy it. Do not invent the hostname.
```

A call to that URL needs your key in the `X-api-key` header. A call with no key returns 401. Copy the URL from `pxt service list` and add the route path. The local service you already called needs no key.

## 6. Insert a video and see the rows

Ask your agent to run the pipeline on a test video:

```
Insert a test video, run the pipeline, and show me the rows.
```

The database runs every stage — detect, match, crop, reframe — and fills in the computed columns. See
the rows for yourself:

```bash
pxt rows /dicer/jobs                         # local
pxt rows pxt://<your-org>:main/dicer/jobs    # cloud. Use :dicer here if that is the database from section 5.
pxt dashboard                                # the local table, on this machine
```

The hosted table is on the [Cloud dashboard](https://www.pixeltable.com/dashboard). `pxt dashboard` opens a page on this machine and starts on your local tables.

A real video in, a reframed video out, every stage visible as its own column.
