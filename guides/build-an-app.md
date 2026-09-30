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

## 2. Ask for a plan

Give your agent this prompt. This is phase 1. The agent reads the spec and stops. It does not run `pxt`.

```
Read spec/autocropper-spec.md and AGENTS.md.

Do phase 1 only. Propose a plan. Do not edit files. Do not run pxt. Stop.
```

## 3. Build it on your machine

Review the plan. If it suits you, send phase 2. This stays on your machine. The agent does not deploy.

```
Do phase 2 from AGENTS.md only. The target is the local path /crop. Do not run pxt db. Do not use a pxt:// URI. Stop after the local curl and the rows.
```

Your agent writes one `app.py`, creates the tables at `/crop`, and starts the service there. Local runs need no image build. When it finishes, check its work.

## 4. Run it on your machine

All local, no cloud, no build. Look at what the agent wrote:

```bash
cat app.py
```

Apply the schema — the `schema` verbs touch only the tables:

```bash
pxt schema diff   app.py /crop       # preview the tables
pxt schema update app.py /crop       # create them
pxt ls /crop                         # they're there
```

Then start the service — the `service` verbs touch only the routes over those tables:

```bash
pxt service diff   app.py /crop      # preview the routes; exit 2 means it would start the service
pxt service update app.py /crop -f   # start the service
```

You now have local endpoints. `pxt service list /crop` prints the URL. A call to that URL needs no key. Try a route from that list, or post a video and get the reframed result back. Fix anything here, locally, before the cloud.

## 5. Deploy the same app to the cloud

Sign in first if you have not (`pxt login` in the README). The agent will not open the browser for you.

When the local curl looks right, send phase 3:

```
Do phase 3 from AGENTS.md only. The local result is good. Deploy the same app.py. Stop after the hosted rows and the service URL.
```

Same `app.py`. A `pxt login` session is enough for this deploy. You do not need an API key until you call the hosted URL.

Keep the local database entry from `pxt init`. Add a second entry. This repo uses `pyproject.toml`, so the section name is `tool.pixeltable.database`.

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:main'
```

`main` is the database `pxt org create` made. If `main` already has another project, such as the quickstart, use a new name instead, for example `pxt://<your-org>:crop`. Do not update `main` in that case. `pxt db update` creates a database that does not exist yet. On `main`, it uploads this project onto the database that is already there.

The commands split across two addresses. `pxt db` takes the database URI, `pxt://<org>:<db>`, and it rejects a URI that also has a catalog path. `pxt schema` and `pxt service` take that path, which is the database URI plus a directory you pick, such as `/crop`.

`pxt db update` uploads the project files and rebuilds the image only when the Python environment changed. The environment is the lockfile, the Python version, and any system packages. The first image build takes several minutes. A later edit to `app.py` is an upload, and it does not rebuild the image. The upload has to happen before `schema update`. The hosted database runs your functions from those files. If you skip the upload, `service diff` says the database has to change first and names `pxt db update` as the next command.

```bash
DB=pxt://<your-org>:main                 # or pxt://<your-org>:crop if main is already in use
PATH=$DB/crop                           # a catalog directory you pick

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

## 6. Check the rows

Phase 3 already inserted one test video. The database fills in each stage as its own column. See the rows yourself:

```bash
pxt rows /crop/jobs                         # local
pxt rows pxt://<your-org>:main/crop/jobs    # cloud. Use :crop here if that is the database from phase 3.
pxt dashboard                                # the local table, on this machine
```

The hosted table is on the [Cloud dashboard](https://www.pixeltable.com/dashboard). `pxt dashboard` opens a page on this machine and starts on your local tables.

A real video in, a reframed video out, every stage visible as its own column.
