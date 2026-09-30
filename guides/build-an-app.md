# Build a real app with your coding agent

You send a video and a product name. The table holds the cropped video. A call to the service returns a URL for that file. Your agent writes the app and runs it on your machine first. You watch the video, call the service, and check the result before you deploy. The cloud copy is the same `app.py`. Only the target changes, from a local name to a `pxt://` URI.

## 1. Choose an app to build

Your agent will need an app spec. You can use one we already wrote with one of our design partners, or
supply your own.

- The autocropper. You insert a video and a product name. The app crops the video around that product, at a target shape such as 9:16. The spec is `spec/autocropper-spec.md`.
- Your own app. Anything that turns media into something you can open again, such as a transcript you can read.

## 2. Ask for a plan

Give your agent this prompt. This is phase 1. The agent reads the spec and stops. It does not run `pxt`.

```
Read spec/autocropper-spec.md and AGENTS.md.

Do phase 1 only. Propose a plan. Do not edit files. Do not run pxt. Stop.
```

## 3. Build it on your machine

Review the plan. If it suits you, send phase 2. This stays on your machine. The agent does not deploy.

```
Do phase 2 from AGENTS.md only. The target is the local path /crop. Do not run pxt db. Do not use a pxt:// URI. Stop after the local curl, the rows, and the path or URL of the cropped video.
```

Your agent writes one `app.py`, creates the tables at `/crop`, and starts the service there. Local runs need no image build. When it finishes, check its work.

## 4. Run it on your machine

All local, no cloud, no build. Look at what the agent wrote:

```bash
cat app.py
```

Apply the schema. The `schema` commands change only the tables:

```bash
pxt schema diff   app.py /crop       # preview the tables
pxt schema update app.py /crop       # create them
pxt ls /crop                         # they're there
```

Then start the service. The `service` commands change only the routes over those tables:

```bash
pxt service diff   app.py /crop      # preview the routes; exit 2 means it would start the service
pxt service update app.py /crop -f   # start the service
```

## 5. See it, use it, and test it

The service is on this machine. Do these three checks before you deploy. A call here needs no API key.

See the cropped video.

```bash
pxt rows /crop/jobs
pxt describe /crop/jobs
pxt dashboard
```

`pxt rows` prints a file path for the video column. Open that path in a video player. `pxt describe` lists the column names. The table is `jobs`, in the directory `crop`. Play `reframed` if that column is there. If the video column has another name, play that column.

`pxt dashboard` prints a URL on this machine and opens it. In the sidebar, open `crop`, then `jobs`, and play the video column. If the page was already open, refresh it so `crop` shows up.

Use the service.

```bash
pxt service list /crop
curl -sS http://127.0.0.1:<port>/jobs
```

Copy the URL from `pxt service list`. `<port>` is the port on that line. Add `/jobs`. The response is JSON. The video field is a URL. Open that URL. It is the same file as the path from `pxt rows`.

Test the result.

The row shows the product you sent and the class the app matched. The cropped video should show that product. The detector uses the first frame. If that frame does not contain the product, the matched class is `none`. Use a video whose first frame shows the product, and insert again.

Fix anything here before the cloud.

## 6. Deploy the same app to the cloud

Sign in first if you have not (`pxt login` in the README). The agent will not open the browser for you.

When the local curl looks right, send phase 3:

```
Do phase 3 from AGENTS.md only. The local result is good. Deploy the same app.py. Stop after the hosted rows, the service URL, and the URL of the cropped video.
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

## 7. See it, use it, and test it on the hosted service

Phase 3 already inserted one test video. Call the hosted route, then watch the video.

Copy the URL from `pxt service list`. A call with no key returns 401. Send your key in `X-api-key`.

```bash
curl -sS "$SERVICE_URL/jobs" \
  -H "X-api-key: $PIXELTABLE_API_KEY"
```

The JSON video field is a URL. Open it.

```bash
pxt rows pxt://<your-org>:main/crop/jobs
```

Use `:crop` in that URI if phase 3 used the database `crop` instead of `main`. `pxt rows` prints a path or a URL for the video column. Open it.

The hosted table is on the [Cloud dashboard](https://www.pixeltable.com/dashboard). Open the directory `crop`, then the table `jobs`, and play the video column. `pxt dashboard` is the local page. It opens your local tables, not this hosted table.
