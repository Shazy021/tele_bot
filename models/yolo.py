import cv2
from PIL import Image
from ultralytics import YOLO
import numpy as np


class YOLOv8:

    def __init__(self, img_path: str = './data/test.png'):
        self.img_path = img_path
        self.model = YOLO('./models/yolov8l.pt')
        self.img = Image.open(self.img_path)
        self.img = np.asarray(self.img)
        self.res_labels = []

        yolo_results = self.model.predict(self.img_path)
        self.__plot_bboxes(self.img, yolo_results[0].boxes.boxes, conf=0.5)

    def __box_label(self, image, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        lw = max(round(sum(image.shape) / 2 * 0.003), 2)
        p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(image, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)
        if label:
            tf = max(lw - 1, 1)  # font thickness
            w, h = cv2.getTextSize(label, 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
            outside = p1[1] - h >= 3
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            cv2.rectangle(image, p1, p2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(image,
                        label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                        0,
                        lw / 3,
                        txt_color,
                        thickness=tf,
                        lineType=cv2.LINE_AA)

    def __plot_bboxes(self, image, boxes, labels=[], colors=[], score=True, conf=None):
        # COCO Labels
        if labels == []:
            labels = {0: u'person', 1: u'bicycle', 2: u'car', 3: u'motorcycle', 4: u'airplane',
                      5: u'bus', 6: u'train', 7: u'truck', 8: u'boat', 9: u'traffic_light', 10: u'fire hydrant',
                      11: u'stop_sign', 12: u'parking_meter', 13: u'bench', 14: u'bird', 15: u'cat', 16: u'dog',
                      17: u'horse', 18: u'sheep', 19: u'cow', 20: u'elephant', 21: u'bear', 22: u'zebra',
                      23: u'giraffe',
                      24: u'backpack', 25: u'umbrella', 26: u'handbag', 27: u'tie', 28: u'suitcase', 29: u'frisbee',
                      30: u'skis', 31: u'snowboard', 32: u'sports_ball', 33: u'kite', 34: u'baseball_bat',
                      35: u'baseball_glove', 36: u'skateboard', 37: u'surfboard', 38: u'tennis_racket', 39: u'bottle',
                      40: u'wine_glass', 41: u'cup', 42: u'fork', 43: u'knife', 44: u'spoon', 45: u'bowl',
                      46: u'banana',
                      47: u'apple', 48: u'sandwich', 49: u'orange', 50: u'broccoli', 51: u'carrot', 52: u'hot dog',
                      53: u'pizza', 54: u'donut', 55: u'cake', 56: u'chair', 57: u'couch', 58: u'potted_plant',
                      59: u'bed',
                      60: u'dining_table', 61: u'toilet', 62: u'tv', 63: u'laptop', 64: u'mouse', 65: u'remote',
                      66: u'keyboard', 67: u'cell_phone', 68: u'microwave', 69: u'oven', 70: u'toaster', 71: u'sink',
                      72: u'refrigerator', 73: u'book', 74: u'clock', 75: u'vase', 76: u'scissors', 77: u'teddy bear',
                      78: u'hair drier', 79: u'toothbrush'}
        # Define colors
        if colors == []:
            colors = [(67, 161, 255), (19, 222, 24), (186, 55, 2), (167, 146, 11), (190, 76, 98),
                      (130, 172, 179), (115, 209, 128), (204, 79, 135), (136, 126, 185), (209, 213, 45), (44, 52, 10),
                      (101, 158, 121), (179, 124, 12), (25, 33, 189), (45, 115, 11), (73, 197, 184), (62, 225, 221),
                      (32, 46, 52), (20, 165, 16), (54, 15, 57), (12, 150, 9), (10, 46, 99), (94, 89, 46),
                      (48, 37, 106), (42, 10, 96), (7, 164, 128), (98, 213, 120), (40, 5, 219), (54, 25, 150),
                      (251, 74, 172), (0, 236, 196), (21, 104, 190), (226, 74, 232), (120, 67, 25), (191, 106, 197),
                      (8, 15, 134), (21, 2, 1), (142, 63, 109), (133, 148, 146), (187, 77, 253), (155, 22, 122),
                      (218, 130, 77), (164, 102, 79), (43, 152, 125), (185, 124, 151), (95, 159, 238), (128, 89, 85),
                      (228, 6, 60), (6, 41, 210), (11, 1, 133), (30, 96, 58), (230, 136, 109), (126, 45, 174),
                      (164, 63, 165), (32, 111, 29), (232, 40, 70), (55, 31, 198), (148, 211, 129), (10, 186, 211),
                      (181, 201, 94), (55, 35, 92), (129, 140, 233), (70, 250, 116), (61, 209, 152), (216, 21, 138),
                      (100, 0, 176), (3, 42, 70), (151, 13, 44), (216, 102, 88), (125, 216, 93), (171, 236, 47),
                      (253, 127, 103), (205, 137, 244), (193, 137, 224), (36, 152, 214), (17, 50, 238), (154, 165, 67),
                      (114, 129, 60), (119, 24, 48), (73, 8, 110)]

        # plot each boxes
        for box in boxes:
            # add score in label if score=True
            if score:
                label = labels[int(box[-1])] + " " + str(round(100 * float(box[-2]), 1)) + "%"
            else:
                label = labels[int(box[-1])]
            # filter every box under conf threshold if conf threshold setted
            if conf:
                if box[-2] > conf:
                    color = colors[int(box[-1])]
                    self.__box_label(image, box, label, color)
            else:
                color = colors[int(box[-1])]
                self.__box_label(image, box, label, color)

            self.res_labels.append(labels[int(box[-1])])

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        cv2.imwrite('./data/result.png', image)
