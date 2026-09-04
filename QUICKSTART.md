# Quickstart: a cloud-hosted table in two minutes

Your org comes with a database named `main`, so you can skip database setup: declare a table straight
into it, insert a row, and read back a column the cloud computed.

You need two things: the `pixeltable` client installed, and your API key set.

```bash
pip install 'pixeltable[serve]==0.7.5'         # ~500MB; a virtualenv is recommended
export PIXELTABLE_API_KEY=sk_...               # your key from https://www.pixeltable.com/dashboard
pxt org list                                   # prints your org slug
```

Save this as `quickstart.py`, with your org slug in place of `<your-org>`, and run it with
`python quickstart.py`:

```python
import pixeltable as pxt

docs = pxt.create_table('pxt://<your-org>:main/quickstart',
                        {'title': pxt.String}, if_exists='replace')
docs.add_computed_column(title_upper=docs.title.upper())   # the database computes this column
docs.insert([{'title': 'hello world'}])
print(docs.select(docs.title, docs.title_upper).collect())
# title='hello world'   title_upper='HELLO WORLD'
```

The table and its computed column live in your `main` database, not on your machine. You created no
database and ran no server.

Next:

- **JAM.md** builds one step by step — your own database, a view, and an HTTP API.
- **CLOUD_QUICKSTART.md** is the reference for building and deploying your own app.
