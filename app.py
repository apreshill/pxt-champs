import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

TableModel = pxt.model_base()


class Docs(TableModel, name='docs'):
    title: pxt.String
    body: pxt.String | None
    title_upper = pxtf.string.upper(title)


ingest = FastAPIRouter(name='ingest')
ingest.add_insert_route(
    Docs,
    path='/docs',
    inputs=[Docs.title, Docs.body],
    outputs=[Docs.title, Docs.title_upper],
)
