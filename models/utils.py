import numpy as np
import cv2

class_names = {0: u'person', 1: u'bicycle', 2: u'car', 3: u'motorcycle', 4: u'airplane',
               5: u'bus', 6: u'train', 7: u'truck', 8: u'boat', 9: u'traffic_light', 10: u'fire hydrant',
               11: u'stop_sign', 12: u'parking_meter', 13: u'bench', 14: u'bird', 15: u'cat', 16: u'dog',
               17: u'horse', 18: u'sheep', 19: u'cow', 20: u'elephant', 21: u'bear', 22: u'zebra', 23: u'giraffe',
               24: u'backpack', 25: u'umbrella', 26: u'handbag', 27: u'tie', 28: u'suitcase', 29: u'frisbee',
               30: u'skis', 31: u'snowboard', 32: u'sports_ball', 33: u'kite', 34: u'baseball_bat',
               35: u'baseball_glove', 36: u'skateboard', 37: u'surfboard', 38: u'tennis_racket', 39: u'bottle',
               40: u'wine_glass', 41: u'cup', 42: u'fork', 43: u'knife', 44: u'spoon', 45: u'bowl', 46: u'banana',
               47: u'apple', 48: u'sandwich', 49: u'orange', 50: u'broccoli', 51: u'carrot', 52: u'hot dog',
               53: u'pizza', 54: u'donut', 55: u'cake', 56: u'chair', 57: u'couch', 58: u'potted_plant', 59: u'bed',
               60: u'dining_table', 61: u'toilet', 62: u'tv', 63: u'laptop', 64: u'mouse', 65: u'remote',
               66: u'keyboard', 67: u'cell_phone', 68: u'microwave', 69: u'oven', 70: u'toaster', 71: u'sink',
               72: u'refrigerator', 73: u'book', 74: u'clock', 75: u'vase', 76: u'scissors', 77: u'teddy bear',
               78: u'hair drier', 79: u'toothbrush'}

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


def nms(boxes, scores, iou_threshold):
    # Sort by score
    sorted_indices = np.argsort(scores)[::-1]

    keep_boxes = []
    while sorted_indices.size > 0:
        # Pick the last box
        box_id = sorted_indices[0]
        keep_boxes.append(box_id)

        # Compute IoU of the picked box with the rest
        ious = compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])

        # Remove boxes with IoU over the threshold
        keep_indices = np.where(ious < iou_threshold)[0]

        sorted_indices = sorted_indices[keep_indices + 1]

    return keep_boxes


def compute_iou(box, boxes):
    # Compute xmin, ymin, xmax, ymax for both boxes
    xmin = np.maximum(box[0], boxes[:, 0])
    ymin = np.maximum(box[1], boxes[:, 1])
    xmax = np.minimum(box[2], boxes[:, 2])
    ymax = np.minimum(box[3], boxes[:, 3])

    # Compute intersection area
    intersection_area = np.maximum(0, xmax - xmin) * np.maximum(0, ymax - ymin)

    # Compute union area
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - intersection_area

    # Compute IoU
    iou = intersection_area / union_area

    return iou


def xywh2xyxy(x):
    # Convert bounding box (x, y, w, h) to bounding box (x1, y1, x2, y2)
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def draw_detections(image, boxes, scores, class_ids, mask_alpha=0.3, mask_maps=None):
    img_height, img_width = image.shape[:2]
    size = min([img_height, img_width]) * 0.0006
    text_thickness = int(min([img_height, img_width]) * 0.001)

    mask_img = draw_masks(image, boxes, class_ids, mask_alpha, mask_maps)

    # Draw bounding boxes and labels of detections
    labels = []
    for box, score, class_id in zip(boxes, scores, class_ids):
        color = colors[class_id][::-1]

        x1, y1, x2, y2 = box.astype(int)

        # Draw rectangle
        cv2.rectangle(mask_img, (x1, y1), (x2, y2), color, 2)

        label = class_names[class_id]
        labels.append(label)
        caption = f'{label} {int(score * 100)}%'
        (tw, th), _ = cv2.getTextSize(text=caption, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                      fontScale=size, thickness=text_thickness)
        th = int(th * 1.2)

        cv2.rectangle(mask_img, (x1, y1),
                      (x1 + tw, y1 - th), color, -1)

        cv2.putText(mask_img, caption, (x1, y1),
                    cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)

    return mask_img


def draw_masks(image, boxes, class_ids, mask_alpha=0.3, mask_maps=None):
    mask_img = image.copy()

    # Draw bounding boxes and labels of detections
    for i, (box, class_id) in enumerate(zip(boxes, class_ids)):
        color = colors[class_id][::-1]

        x1, y1, x2, y2 = box.astype(int)

        # Draw fill mask image
        if mask_maps is None:
            cv2.rectangle(mask_img, (x1, y1), (x2, y2), color, -1)
        else:
            crop_mask = mask_maps[i][y1:y2, x1:x2, np.newaxis]
            crop_mask_img = mask_img[y1:y2, x1:x2]
            crop_mask_img = crop_mask_img * (1 - crop_mask) + crop_mask * color
            mask_img[y1:y2, x1:x2] = crop_mask_img

    return cv2.addWeighted(mask_img, mask_alpha, image, 1 - mask_alpha, 0)


def draw_comparison(img1, img2, name1, name2, fontsize=2.6, text_thickness=3):
    (tw, th), _ = cv2.getTextSize(text=name1, fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                  fontScale=fontsize, thickness=text_thickness)
    x1 = img1.shape[1] // 3
    y1 = th
    offset = th // 5
    cv2.rectangle(img1, (x1 - offset * 2, y1 + offset),
                  (x1 + tw + offset * 2, y1 - th - offset), (0, 115, 255), -1)
    cv2.putText(img1, name1,
                (x1, y1),
                cv2.FONT_HERSHEY_DUPLEX, fontsize,
                (255, 255, 255), text_thickness)

    (tw, th), _ = cv2.getTextSize(text=name2, fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                  fontScale=fontsize, thickness=text_thickness)
    x1 = img2.shape[1] // 3
    y1 = th
    offset = th // 5
    cv2.rectangle(img2, (x1 - offset * 2, y1 + offset),
                  (x1 + tw + offset * 2, y1 - th - offset), (94, 23, 235), -1)

    cv2.putText(img2, name2,
                (x1, y1),
                cv2.FONT_HERSHEY_DUPLEX, fontsize,
                (255, 255, 255), text_thickness)

    combined_img = cv2.hconcat([img1, img2])
    if combined_img.shape[1] > 3840:
        combined_img = cv2.resize(combined_img, (3840, 2160))

    return combined_img
