# Build a real app with your coding agent

Build a real application with your coding agent — a video autocropper, or your own. Your agent writes
it and runs it, first on your machine, then in the cloud. It is the same app both times; only the
target changes, from a local name to a `pxt://` URI. Your job is to say what to build, then check the
agent's work at each step.

## 1. Choose an app to build

Your agent will need an app spec. You can use one we already wrote with one of our design partners, or
supply your own.

- **The autocropper** — insert a video and a product name, and the app returns the video reframed to a
  target shape (say 9:16 for vertical), cropped around that product. Its full spec is in
  `autocropper-spec.md`.
- **Your own app** — anything that turns media into something useful: search a library of images by
  description, transcribe and summarize calls, pull structured fields out of documents, generate images
  from prompts.

## 2. Hand the spec to your agent

To build the autocropper, give your agent this prompt to start:

```
Take a look at guides/autocropper-spec.md

Propose a plan for how to create a service with Pixeltable for this.

Rules: Use the Pixeltable CLI. Use class-based schemas. Write to a single `app.py` file. Always prefer
built-in UDFs and UDAs over custom.

Read `AGENTS.md` in this repo and follow it for every `pxt` command.

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

You now have local endpoints. Open the service's `/docs` in a browser to try a route, or post a video
and get the reframed result back. Fix anything here, locally, before the cloud.

## 5. Deploy the same app to the cloud

Same `app.py`. The commands split across two addresses. `pxt db` takes the database URI, `pxt://<org>:<db>`,
and it rejects a URI that also has a catalog path. `pxt schema` and `pxt service` take that path, which is
the database URI plus a directory you pick, such as `/dicer`.

`pxt db update` creates the database if it does not exist yet, uploads the project files, and rebuilds the
image only when the Python environment changed. The environment is the lockfile, the Python version, and
any system packages. The first image build takes several minutes. A later edit to `app.py` is an upload,
and it does not rebuild the image.

Do this before `schema update`. The hosted database runs your functions from those uploaded files. If you
skip the upload, `service diff` says the database has to change first and names `pxt db update` as the next
command.

```bash
DB=pxt://<your-org>:<db>                 # the hosted database
PATH=$DB/dicer                           # a catalog directory you pick

pxt db diff   $DB                        # preview; exit 2 means there is something to apply
pxt db update $DB -f                     # create, upload, and build the image if the environment changed

pxt schema diff   app.py $PATH           # same preview as local, cloud target
pxt schema update app.py $PATH           # create the tables

pxt ls       $PATH                       # the tables are there
pxt cd       $PATH                       # make that directory your working location
pxt describe jobs                        # inspect a table (relative path, after cd)
```

Serving in the cloud is the same two commands as on your machine. Start the service, then read its
public URL:

```bash
pxt service diff   app.py $PATH          # preview; exit 2 means it would start the service
pxt service update app.py $PATH -f
pxt service list   $PATH                 # prints the https://... service URL
```

Then open that URL's `/docs`, or post a video from anywhere — the same app, on your machine and in the
cloud.

## 6. Insert a video and see the rows

Ask your agent to run the pipeline on a test video:

```
Insert a test video, run the pipeline, and show me the rows.
```

The database runs every stage — detect, match, crop, reframe — and fills in the computed columns. See
the rows for yourself:

```bash
pxt rows /dicer/jobs                         # local
pxt rows pxt://<your-org>:<db>/dicer/jobs    # the same table in the cloud
pxt dashboard                                # watch the pipeline run, and play the reframed video
```

A real video in, a reframed video out, every stage visible as its own column.
