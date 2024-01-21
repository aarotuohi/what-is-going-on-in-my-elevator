import cv2
import numpy as np
import os
from yolo.centroidtracker import CentroidTracker
from yolo.trackableobject import TrackableObject

# Get the directory that this script is in
dir_path = os.path.dirname(os.path.realpath(__file__))

# CONF_THRESHOLD is the minimum probability to filter weak detections.
# It is used to discard detections with a confidence score less than this threshold.
CONF_THRESHOLD = 0.65

# NMS_THRESHOLD is the threshold for the non-maximum suppression algorithm, 
# which eliminates redundant overlapping bounding boxes. 
# A lower value means suppressing more.
NMS_THRESHOLD = 0.30

# Construct the path to the yoloclasses.txt file
CLASSES_FILE = os.path.join(dir_path, 'yoloclasses.txt')
WEIGHT_FILE = os.path.join(dir_path, 'conf_and_weights/all_colormapJET_final.weights')
CONFIG_FILE = os.path.join(dir_path, 'conf_and_weights/all_colormapJET.cfg')

class ObjectDetector:
    def __init__(self):
        self.net = cv2.dnn.readNet(WEIGHT_FILE, CONFIG_FILE)
        with open(CLASSES_FILE, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.colors = np.array([[0, 250, 150]])
        # Generate random colors for the remaining classes
        if len(self.classes) > 1:
            self.colors = np.append(self.colors, np.random.uniform(0, 255, size=(len(self.classes) - 1, 3)), axis=0)
        self.ct = CentroidTracker(maxDisappeared=1, maxDistance=50)
        self.trackers = []
        self.trackableObjects = {}
        self.totalDown = 0
        self.totalUp = 0
        self.change = 0

    def detectObjects(self, img, track):
        img = cv2.resize(img, (448, 256))
        Height, Width = img.shape[:2]
        scale = 1/255
        blob = cv2.dnn.blobFromImage(img, scale, (448, 256), (0,0,0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers())
        class_ids, confidences, boxes = self.process_detections(outs, Width, Height, CONF_THRESHOLD)
        indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)
        self.draw_predictions(img, indices, class_ids, confidences, boxes, track)
        return img
    
    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        return output_layers
    
    def process_detections(self, outs, Width, Height, CONF_THRESHOLD):
        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > CONF_THRESHOLD:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        return class_ids, confidences, boxes

 
    def draw_predictions(self, img, indices, class_ids, confidences, boxes, track):
        rects = []
        for i in indices:
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            if class_ids[i] == 0:
                rects.append((left, top, left + width, top + height))
                # use the centroid tracker to associate the (1) old object
                # centroids with (2) the newly computed object centroids
                if track:
                    objects = self.ct.update(rects)
                    self.counting(objects, img)
            draw_predict(img, self.classes, self.colors, class_ids[i], confidences[i], round(left), round(top), round(left + width), round(top + height))
        cv2.putText(img, f'{len(indices)}', (5, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (60, 50, 250), 2)
        if track:
            info = [
                ("Up", self.totalUp),
                ("Down", self.totalDown),
                ("Change", self.change ),
                ("Detection", len(indices)),
            ]

            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):

                text = "{}".format(v)
                if k == "Change":
                    cv2.putText(img, f'Change : {text}', (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                if k == 'Up':
                    cv2.putText(img, f'Up : {text}', (10, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                if k == 'Down':
                    cv2.putText(img, f'Down : {text}', (10, 95),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                if k == 'Detection':
                    cv2.putText(img, f'Detection : {text}', (10, 115),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.line(img, (0, img.shape[0] // 2), (img.shape[1], img.shape[0] // 2), (0, 255, 0), 2)


    def counting(self, objects, img):
        global change

        for (objectID, centroid) in objects.items():
            to = self.trackableObjects.get(objectID, None)
            direction = None
            if to is None:
                to = TrackableObject(objectID, centroid)
            else:  
                direction = check_direction(to, centroid)
                to.centroids.append(centroid)
                self.count_objects(to, direction, centroid, img)
                self.change = np.abs(self.totalUp - self.totalDown)
            self.trackableObjects[objectID] = to
            draw_object_id_and_centroid(img, objectID, centroid, direction)
            
    def count_objects(self, to, direction, centroid, img):
        center_line = img.shape[0] // 2

        if not to.counted:
            if direction < 0 and centroid[1] < center_line:
                self.totalUp += 1
                to.counted = True
            elif direction > 0 and centroid[1] > center_line:
                self.totalDown += 1
                to.counted = True
        elif to.counted:
            if direction < 0 and centroid[1] > center_line:
                to.counted = False
            elif direction > 0 and centroid[1] < center_line:
                to.counted = False


def draw_predict(img, classes, colors, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id]) + " : " + "{:.2f}".format(confidence)
    color = tuple(map(int, colors[class_id]))
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def check_direction(to, centroids):
    y = [c[1] for c in to.centroids]
    direction = centroids[1] - np.mean(y)
    return direction



def draw_object_id_and_centroid(img, objectID, centroid, direction):
    if direction is None:
        color = (255, 0, 0)  
    elif(direction > 0):
        color = (0, 0, 255)
    else:
        color = (0, 255, 0)
    text = "ID {}".format(objectID)
    cv2.putText(img, text, (centroid[0] - 10, centroid[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.circle(img, (centroid[0], centroid[1]), 4, color, -1)
