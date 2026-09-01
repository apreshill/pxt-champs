import pixeltable as pxt

TableModel = pxt.model_base()


class Items(TableModel, name='items'):
    title: pxt.String
    note: pxt.String | None
