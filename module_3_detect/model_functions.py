from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

labels = {0: 'hand', 1: 'person', 2: 'pizza', 3: 'scooper'}

## Intialize model

model = YOLO("yolo12m-v2.pt") 
tracker = DeepSort(max_age=30,n_init=3,override_track_class=False ) 


def get_boxes_by_labels(predictions):
    '''
    Clean yolo output by return dictionary map of label to boxes of that label
    '''
    selected_boxes = {label: [] for label in labels.values()} 

    for res in predictions:  
        boxes = getattr(res.boxes, "xyxy", None)
        cls = getattr(res.boxes, "cls", None)


        if boxes is None or cls is None:
            continue

        
        try:
            b = boxes.cpu().numpy()
            c = cls.cpu().numpy()
        except Exception:
            b = boxes.numpy()
            c = cls.numpy()


        for box, label in zip(b, c):
            selected_boxes[labels[int(label)]].append(box)

    return selected_boxes


def update_tracker( predictions,frame):
    '''
    For Deep sort do an one step update using predications with frame
    '''
    detections = []
    for res in predictions:  
        boxes = getattr(res.boxes, "xyxy", None)
        conf = getattr(res.boxes, "conf", None)
        cls = getattr(res.boxes, "cls", None)

        
        if boxes is None or conf is None:
            continue

        try:
            b = boxes.cpu().numpy()
            f = conf.cpu().numpy()
            c = cls.cpu().numpy()

        except Exception:
            b = boxes.numpy()
            f = conf.numpy()
            c = cls.numpy()


        
        for box , conf,label in zip(b, f,c):
            x1, y1, x2, y2 = box
            detections.append(([x1, y1, x2-x1, y2-y1], conf, labels[int(label)]))

        
        tracks = tracker.update_tracks(detections, frame=frame)
    return tracks, detections

