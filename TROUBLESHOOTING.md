# Troubleshooting

Real errors from real runs, with the cause and the fix. Most of these cost our first beta tester
time before they figured them out. You should not have to.

## `invalid choice: 'create'` when I run `pxt db create`

There is no `pxt db create`. Creating a cloud database is declarative: you describe it in
`pyproject.toml` and apply that. See "Create a second database" below. The verbs `pxt db` actually
has are `diff`, `update`, `list`, `status`, `start`, `stop`, `build-image`, `delete`. Run
`pxt db --help` to see them.

## `pxt status` says `total_tables=0` but I created tables

`pxt status` reports the local daemon on your laptop, not the cloud. Your cloud tables are fine. To
see the cloud, address it by its URI:

```bash
pxt ls --tree pxt://<your-org>:champs      # the tables and views in this project's directory
pxt db status pxt://<your-org>:champs --json   # AVAILABLE, worker health
```

The `pxt://` prefix is what routes a command to the cloud instead of your laptop.

## `pxt ls -r` is rejected

There is no `-r` flag. Use `--tree`:

```bash
pxt ls --tree pxt://<your-org>:champs
```

## `pxt db diff` proposes a rebuild again, right after a successful update

Known behavior in 0.7.4. The control plane does not return a fingerprint, so `diff` cannot tell that
the last `update` already applied. It is not an error and your database is fine. Run `pxt db status`
to confirm the database is `AVAILABLE`.

## An error mentions `pixeltable_source` or an unexpected field in `pixeltable.toml`

A `[pixeltable.database.pixeltable_source]` git pin (a `git = ...` / `rev = ...` block) is from an
older setup and 0.7.4 rejects it. This repo installs Pixeltable from PyPI and has no such block.
If you copied config from an older project, delete that block.

## `This feature requires the 'spacy' package` when I split text

`string_splitter` only supports sentence splitting, which needs spaCy plus a model download. This
repo splits audio instead (`audio_splitter`), which needs nothing extra. If you do want
sentence splitting, `pip install -U spacy` first.

## Notebook 04 fails to import `torch` or `transformers`

Notebook 04 (CLIP image search) is the one optional heavy step. Install its extras first:

```bash
uv sync --extra clip
```

This installs `torch` and `transformers` and downloads the CLIP model (~600MB) on first run. The
rest of the repo needs none of it.

## Create another database

The notebooks create one database (`champs`). To add another, put a second block in `pyproject.toml`
and run `pxt db update` against it:

```toml
[[tool.pixeltable.database]]
name = 'pxt://<your-org>:scratch'
python_version = '3.12'
cpu = 0.5
memory_mb = 512
disk_gb = 10
workers = 1
```

Then:

```bash
pxt db diff pxt://<your-org>:scratch     # shows "resolution": "create"
pxt db update pxt://<your-org>:scratch   # builds and deploys, 10+ minutes on first run
pxt db status pxt://<your-org>:scratch --json    # wait for AVAILABLE
```

Note: the Community plan allows one database. Creating a second needs a plan that permits it.

## First `pxt db update` takes 10+ minutes

Expected. It builds a runtime image and deploys workers. Watch it with
`pxt db status pxt://<your-org>:<db> --json` until the build state reads `SUCCEEDED` and the database
reads `AVAILABLE`.
