# AGENTS.md

You are helping someone use **Pixeltable Cloud**, the beta for cloud-hosted tables. Most people
here are new to Pixeltable. Read this whole file before you run anything. It gives you the mental
model, equips you, routes you, and lists the traps that waste time.

## Step 0: equip yourself

Do these first, once:

1. Add the Pixeltable agent skill: `npx skills add pixeltable/pixeltable-skill`
2. Connect the docs MCP if your client supports it: `https://docs.pixeltable.com/mcp`
3. Full API reference, if you need it: `https://docs.pixeltable.com/llms-full.txt`

Do not guess Pixeltable APIs from memory. The skill and the docs are current; your training may not be.

## The mental model (hold this, and nothing here is a maze)

**Pixeltable is an OLTP database for multimodal AI apps.** Your media (images, video, audio,
documents), the AI outputs you derive from it, and your app state live in one database and stay
consistent as data changes. Because it is a real database, it gives you guarantees. A failed insert
or model call leaves no partial state, many processes read and write at once, and single-row reads
stay fast enough to serve a live app. The one-word answer to "what is Pixeltable" is *database*.

**The vocabulary is the CLI. Three nouns drive everything:**

- **database** (`db`): where your data lives. A cloud database is addressed `pxt://org:db`. Every
  org starts with one named `main`.
- **schema**: the shape and logic of your data. Which tables exist, each table's columns typed with
  the multimodal type system (`String`, `Image`, `Video`, `Audio`, `Document`, `Json`, scalars),
  and how derived columns are computed from others (a model call, an API call, a transform). You
  write your schema as a class-based Python file. A schema is a database concept.
- **service**: the HTTP endpoints an application file declares, so the database serves over the network.

Inside a schema: a **table** holds rows of multimodal columns; a **column** is stored or derived (a
derived column is `f(other columns)`, kept current on every insert); a **view** derives a table
from another, often by exploding each row into many (one voice note into its segments).

**Every action is one of three things. Tag your steps with which:**

- **[DECLARE]** a table, column, or view. You describe the result you want, and the database maintains it.
- **[INSERT]** data. Each insert is one transaction, so a failure leaves no half-written rows, and the computed columns fill in as the data lands.
- **[LOOK]**. Query what you built with `.collect()`, `pxt ls --tree`, or the dashboard.

The whole repo tells one story: you declare a schema, insert data, and query it, first on your
laptop and then against the same schema in the cloud.

## The CLI is one grammar: `pxt <noun> <verb>`

`schema` and `service` share three verbs:

- `check`: validate the file on its own. No target. Does not look at a catalog.
- `diff`: preview. Show what `update` would change on a target. Exit code 2 means changes are pending.
- `update`: apply. Make the target match your file.

Run `check` before `diff` so a bad file is not confused with a catalog mismatch.

`db` shares `diff` and `update`. It also has lifecycle verbs (`list`, `status`, `start`, `stop`,
`delete`, `build-image`). `schema` and `service` also have `prune` and `example`.

**When unsure of a verb, run `pxt <noun> --help`. Never guess a verb.**

## Where to go

- **Everyone starts here:** `01_setup.ipynb` (reach your cloud database), then `CLOUD_TABLES.md`
  (build cloud-hosted tables). Keep `CHEATSHEET.md` open as a command reference.
- Then, if you want: `03_serve_api.ipynb` (serve your database as an API),
  `04_image_search.ipynb` (optional, image search, installs a large model),
  `05_share_table.ipynb` (optional, share a table).
- Deploying a whole app to its own hosted database (its own deps and services)? `CLOUD_QUICKSTART.md`
  is the tight reference: the `pxt db` / `pxt schema` / `pxt service` `diff`/`update` loop.
- Stuck? `TROUBLESHOOTING.md` has the exact errors and fixes.

## Do not do this (anti-patterns)

Pixeltable replaces these. Reaching for them means you are off-path.

- No LangChain, LlamaIndex, or agent frameworks. Chunking is an iterator. Search is `.similarity()`.
- No pandas as a store. Tables are the store. `.collect().to_pandas()` is export only.
- No `for row in ...` loops calling a model. Wrap the call in a computed column.
- No separate vector database. Use an embedding index on the table.

## CLI reality (these waste an agent's time if you do not know them)

- Use `pxt db update` to create a cloud database. There is no `pxt db create`.
- Use `pxt ls --tree pxt://org:db`. There is no `pxt ls -r`.
- Cloud state comes from `pxt ls --tree` and `pxt db status`, not `pxt status` (that shows the local
  daemon, and will read `total_tables=0` even when your cloud database is full).
- Add `--json` to any inspection or query command and parse that, rather than scraping text.
- Address cloud things by their `pxt://org:db` URI. The prefix is what routes to the cloud.
- A hosted database runs your project. `pxt db update pxt://org:db` builds its image from your
  lockfile and ships it before `pxt schema update` / `pxt service update` can run against it. The
  database must be declared in a `[[tool.pixeltable.database]]` entry.
- Read the org from `pxt org list --json`; do not hardcode an org name.
