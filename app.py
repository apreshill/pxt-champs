import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.functions.openai import chat_completions
from pixeltable.functions.yolox import yolox
from pixeltable.serving import FastAPIRouter

TableModel = pxt.model_base()

# YOLOX label ids are the 80 COCO classes, in this order.
COCO_CLASSES = (
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
    'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle',
    'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
    'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
    'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush',
)


@pxt.udf
def candidate_classes(detections: dict) -> list[str]:
    """Distinct detected class names, highest score first."""
    scores = (detections or {}).get('scores') or []
    labels = (detections or {}).get('labels') or []
    best: dict[str, float] = {}
    for score, label in zip(scores, labels):
        index = int(label)
        if index < 0 or index >= len(COCO_CLASSES):
            continue
        name = COCO_CLASSES[index]
        if float(score) > best.get(name, -1.0):
            best[name] = float(score)
    return [name for name, _score in sorted(best.items(), key=lambda item: item[1], reverse=True)]


@pxt.udf
def match_prompt(product: str, classes: list[str]) -> str:
    listed = ', '.join(classes) if classes else '(none)'
    return (
        f'Product description: {product}\n'
        f'Detected classes: {listed}\n'
        'Reply with one class name copied from the detected classes, or none. No other words.'
    )


@pxt.udf
def choose_class(reply: str, classes: list[str]) -> str:
    text = (reply or '').strip().lower().strip('.')
    for name in classes:
        if text == name.lower():
            return name
    return 'none'


def _even(value: float, limit: int) -> int:
    size = int(round(value))
    if size % 2:
        size -= 1
    size = max(2, min(size, limit if limit % 2 == 0 else limit - 1))
    return size


@pxt.udf
def crop_window(detections: dict, label: str, width: int, height: int, ratio: float) -> list[int]:
    """Fixed crop window as [x, y, width, height], inside the frame, at the target ratio."""
    frame_w = int(width)
    frame_h = int(height)
    target = float(ratio) if ratio and float(ratio) > 0 else frame_w / frame_h

    box = None
    best_score = -1.0
    if label and label != 'none':
        scores = (detections or {}).get('scores') or []
        labels = (detections or {}).get('labels') or []
        bboxes = (detections or {}).get('bboxes') or []
        for bbox, score, detected in zip(bboxes, scores, labels):
            index = int(detected)
            name = COCO_CLASSES[index] if 0 <= index < len(COCO_CLASSES) else ''
            if name == label and float(score) > best_score:
                best_score = float(score)
                box = bbox

    if box is None:
        win_w = frame_w
        win_h = frame_w / target
        if win_h > frame_h:
            win_h = frame_h
            win_w = frame_h * target
        win_w = _even(win_w, frame_w)
        win_h = _even(win_h, frame_h)
        return [(frame_w - win_w) // 2, (frame_h - win_h) // 2, win_w, win_h]

    x1, y1, x2, y2 = (float(v) for v in box)
    box_w = max(x2 - x1, 1.0)
    box_h = max(y2 - y1, 1.0)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    if box_w / box_h < target:
        win_w = box_h * target
        win_h = box_h
    else:
        win_w = box_w
        win_h = box_w / target
    scale = min(1.0, frame_w / win_w, frame_h / win_h)
    win_w = _even(win_w * scale, frame_w)
    win_h = _even(win_h * scale, frame_h)
    origin_x = int(round(center_x - win_w / 2))
    origin_y = int(round(center_y - win_h / 2))
    origin_x = max(0, min(origin_x, frame_w - win_w))
    origin_y = max(0, min(origin_y, frame_h - win_h))
    return [origin_x, origin_y, win_w, win_h]


class Jobs(TableModel, name='jobs'):
    """A video, a product description, and the reframed video cropped around that product."""

    video: pxt.Video
    product: pxt.String
    ratio: pxt.Float
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)

    frame = video.extract_frame(timestamp=0.0)
    detections = yolox(frame, model_id='yolox_s', threshold=0.25)
    classes = candidate_classes(detections)
    response = chat_completions(
        messages=[{'role': 'user', 'content': match_prompt(product, classes)}],
        model='gpt-4o-mini',
        model_kwargs={'temperature': 0},
    )
    reply = response.choices[0].message.content
    matched_class = choose_class(reply, classes)
    window = crop_window(
        detections,
        matched_class,
        frame.get_metadata().width,
        frame.get_metadata().height,
        ratio,
    )
    reframed = video.crop(window, bbox_format='xywh')


@pxt.query
def list_jobs():
    return Jobs.select(Jobs.product, Jobs.matched_class, Jobs.ratio, Jobs.reframed)


api = FastAPIRouter(name='autocrop')
api.add_insert_route(
    Jobs,
    path='/jobs',
    uploadfile_inputs=[Jobs.video],
    inputs=[Jobs.product, Jobs.ratio],
    outputs=[Jobs.matched_class, Jobs.window, Jobs.reframed],
)
api.add_query_route(path='/jobs', query=list_jobs, method='get')
