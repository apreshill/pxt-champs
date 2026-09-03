import pixeltable as pxt

# Set <your-org> to your org slug (champs is the database from step 2).
docs = pxt.get_table('pxt://<your-org>:champs/docs')
docs.insert([{'title': 'hello world', 'body': 'a first doc'}])
print(docs.select(docs.title, docs.title_upper).collect())
