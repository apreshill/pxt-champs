# Build cloud-hosted tables

Create your own hosted database, declare a multimodal schema in it, insert postcards, and watch the
database compute derived columns and split a voice note into segments. No model download and no
provider key. The one slow part is the first image build, which takes 10+ minutes.

Prerequisites: you finished `01_setup.ipynb`, so your API key is set. Replace `<your-org>` below with
your org slug from `pxt org list`, and use the same `<your-org>:champs` in `pyproject.toml`.

## Create and ship your database

`pyproject.toml` declares your database:

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:champs'
```

`pxt db update` creates it and builds a hosted image from your `uv.lock`, so the database runs your
project. `diff` previews, `update` applies. The first build takes 10+ minutes; later edits ship in
seconds.

```bash
pxt db diff   pxt://<your-org>:champs
pxt db update pxt://<your-org>:champs          # first run: create the db, build the image (10+ min)
pxt db status pxt://<your-org>:champs --json   # wait for state AVAILABLE
```

## Write and apply your schema

A **schema** is the shape and logic of your data: which tables exist, each table's columns and their
types, and how the derived columns are computed from other columns. You write it as a class-based
Python file. Yours is `app.py`, a `Postcards` table plus a `Segments` view. Open it and read the
comments first.

`check` validates the file, `diff` shows what would change, and `update` applies it. Then `describe`
prints the result, with each column's type and the expression it is computed from.

```bash
pxt schema check  app.py                           # is the file valid?
pxt schema diff   app.py pxt://<your-org>:champs   # what would change?
pxt schema update app.py pxt://<your-org>:champs   # create the tables and the view

pxt describe pxt://<your-org>:champs/postcards
pxt describe pxt://<your-org>:champs/segments      # the view, plus the base columns it carries
```

## Insert postcards, and the database computes

Each insert is one transaction. When it returns, the computed columns are filled and the `Segments`
view already holds the audio the database split out, with no pipeline code of yours.

```python
import pixeltable as pxt

postcards = pxt.get_table('pxt://<your-org>:champs/postcards')
postcards.insert([
    {'caption': 'wish you were here',       'image': 'data/beach.jpg',   'voice': 'data/beach.wav'},
    {'caption': 'greetings from the pines', 'image': 'data/forest.jpg',  'voice': 'data/forest.wav'},
    {'caption': 'hot out here',             'image': 'data/desert.jpg',  'voice': 'data/desert.wav'},
])
postcards.select(postcards.caption_upper, postcards.width, postcards.thumb).collect()

segments = pxt.get_table('pxt://<your-org>:champs/segments')
segments.select(segments.segment_start, segments.segment_end, segments.seconds).collect()
```

## See it

```bash
pxt ls --tree pxt://<your-org>:champs   # postcards (table), segments (view)
pxt dashboard                           # browse it, with images and audio inline
```

## Build your own

Scaffold a schema with the CLI: `pxt schema example` prints a full one, `--brief` a minimal one, and
`--out my_app.py` writes it to edit and apply. `pxt service example` does the same for routes.

```bash
pxt schema example --brief          # a minimal schema to start from
pxt schema example --out my_app.py  # write it, then edit and apply
```

## What next

- `03_serve_api.ipynb` serves this database as an API.
- `04_image_search.ipynb` searches images by text with CLIP (optional, installs a large model).
- `05_share_table.ipynb` shares a table (optional).

Stuck? `TROUBLESHOOTING.md`.
