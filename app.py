"""Postcards: the pxt-champs example schema and API.

One file holds both halves of a Pixeltable application:
  - the models, which name the tables and declare their columns, and
  - the services, which serve HTTP routes over those tables.

The target on the command line says which database (catalog directory or pxt:// URI) the
tables live in, so the same file applies to your laptop and to the cloud:

    pxt schema update app.py pxt://<org>:main/champs     # create the tables this file declares
    pxt service update app.py pxt://<org>:main/champs    # serve this file's routes against them

Everything here runs with no provider API key and no model download: the computed columns are
text and Pillow image transforms, and the view splits each voice note into segments with
audio_splitter.

Building your own app? The agent skill carries the full API:
    npx skills add pixeltable/pixeltable-skill
"""

import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

TableModel = pxt.model_base()


class Postcards(TableModel, name='postcards'):
    """A postcard: a caption, an image, and a voice note.

    Annotations declare stored columns; assignments declare computed columns the database fills
    in on every insert. None of these call a model, so nothing downloads.
    """

    caption: pxt.String
    image: pxt.Image
    voice: pxt.Audio | None

    caption_upper = pxtf.string.upper(caption)  # text computed column
    thumb = image.thumbnail((200, 200))         # Pillow image computed column, no download
    grayscale = image.convert('L')              # Pillow image computed column, no download
    width = image.width                         # a property of the image, stored as a column


class Segments(
    TableModel,
    name='segments',
    base=Postcards,
    iterator=pxtf.audio.audio_splitter(Postcards.voice, duration=2.0),
):
    """A view: one row per audio segment the iterator cuts from each postcard's voice note.

    An iterator explodes one base row into many. Swap audio_splitter for frame_iterator (video to
    frames) or document_splitter (docs to chunks) and everything else stays the same.
    """

    # 'segment_start', 'segment_end', 'audio_segment' are output columns of the iterator
    seconds = segment_end - segment_start  # type: ignore[name-defined]  # noqa: F821  computed on each segment


# the router names the service
api = FastAPIRouter(name='postcards-api')

# POST /postcards inserts a postcard and returns its computed columns
api.add_insert_route(
    Postcards,
    path='/postcards',
    inputs=[Postcards.caption, Postcards.image],
    outputs=[Postcards.caption_upper, Postcards.width],
)

# POST /shout computes without storing a row
api.add_compute_route(
    Postcards,
    path='/shout',
    inputs=[Postcards.caption],
    outputs=[Postcards.caption_upper],
)
