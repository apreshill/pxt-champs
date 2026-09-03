# Cheatsheet

Quick reference for Pixeltable Cloud. Replace `<org>` with your org slug from `pxt org list`.

## CLI grammar: `pxt <noun> <verb>`

| noun | what it is | main verbs |
|------|-----------|------------|
| `schema` | your tables, columns, views (from a class-based file) | `diff`, `update`, `check`, `example` |
| `db` | a cloud database, `pxt://org:db` | `diff`, `update`, `status`, `list`, `start`, `stop` |
| `service` | HTTP routes an app file declares | `check`, `diff`, `update`, `list`, `stop` |

`check` validates the file. No target. `diff` previews a target. `update` applies. Unsure of a verb? `pxt <noun> --help`.

## The moves

- **declare** a table / column / view (edit `app.py`, then `pxt schema update`)
- **insert** data with `table.insert([...])`, and computed columns fill in automatically
- **look** (`.collect()`, `pxt ls --tree`, `pxt dashboard`)

## Commands you reuse

```bash
pxt org list                                  # your org slug
pxt db update pxt://<org>:champs               # create the database, build + ship its image (10+ min)
pxt db status pxt://<org>:champs --json        # is it live? (AVAILABLE)
pxt schema check app.py                        # is the file valid? (no target)
pxt schema update app.py pxt://<org>:champs    # create/update the tables
pxt ls --tree pxt://<org>:champs               # what's in the database
pxt dashboard                                  # open the web UI
pxt <noun> diff ...                            # preview before you update
```

```python
import pixeltable as pxt
t = pxt.get_table('pxt://<org>:champs/postcards')
t.insert([{'caption': '...', 'image': 'data/beach.jpg', 'voice': 'data/beach.wav'}])
t.select(t.caption_upper, t.width).collect()
```

## Good to know

- Each hosted database is `pxt://<org>:<db>`. `pxt db update` creates it and ships your project's image; then `schema`/`service` `update` run against it.
- `pxt schema check app.py` and `pxt service check app.py` validate the file. Then `diff`, then `update`.
- See your cloud tables with `pxt ls --tree pxt://<org>:champs`.

## Set your key

Persistent, in `~/.pixeltable/config.toml`:

```toml
[pixeltable]
api_key = 'your-api-key'
```

Or per session: `export PIXELTABLE_API_KEY=your-api-key`.

More detail: `CLOUD_TABLES.md` to build, `TROUBLESHOOTING.md` when stuck.
