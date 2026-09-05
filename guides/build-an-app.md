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
pxt service diff   app.py /dicer      # preview the service (errors for now — a bug being fixed)
pxt service update app.py /dicer -f   # start the service
```

You now have local endpoints. Open the service's `/docs` in a browser to try a route, or post a video
and get the reframed result back. Fix anything here, locally, before the cloud.

## 5. Deploy the same app to the cloud

Same `app.py`, same commands — only the target changes, from `/dicer` to your cloud database's URI.
Applying the schema errors the first time: your app's custom UDFs aren't in the hosted image yet.
`pxt db update` rolls the image to include them (several minutes), and then the schema applies:

```bash
URI=pxt://pixeltable:mk-demoday/dicer    # your cloud database, and a path you pick

pxt schema diff   app.py $URI            # same as local, cloud target
pxt schema update app.py $URI            # errors: your custom UDFs aren't in the hosted image yet
pxt db update     $URI                    # rolls the image to include your UDFs (several minutes)
pxt schema update app.py $URI            # now it applies

pxt ls       $URI                        # the tables are there
pxt cd       $URI                        # make the cloud database your working location
pxt describe jobs                        # inspect a table (relative path, after cd)
```

Serving in the cloud is the same two commands as on your machine — start the service, then get its
public URL. This hits the same service bug being fixed, so it wasn't part of the live run; once the fix
lands, these give you a running cloud service:

```bash
pxt service update app.py $URI -f
pxt service list $URI                    # prints the https://... service URL
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
pxt rows /dicer/jobs    # the computed values for each job
pxt dashboard           # watch the pipeline run, and play the reframed video
```

A real video in, a reframed video out, every stage visible as its own column.
