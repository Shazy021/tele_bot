import cv2
from PIL import Image
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
import numpy as np


class Detectron2:
    def __init__(self, img_path: str, conf_thres: float = 0.5):
        self.frame = Image.open(img_path)
        self.frame = cv2.cvtColor(np.array(self.frame, dtype=np.uint8), cv2.COLOR_BGR2RGB)

        # config
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"))
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = conf_thres
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml")
        self.cfg.MODEL.DEVICE = "cuda:0"

        # prediction
        self.outputs, self.panoptic_seg, self.segments_info = self.__predict()

        # visualizer
        self.out, self.classes = self.__visualize(self.outputs, self.panoptic_seg)

        # save img
        cv2.imwrite('./data/detectron.png', self.out.get_image()[:, :, ::-1])

    def __predict(self):
        predictor = DefaultPredictor(self.cfg)
        panoptic_seg, segments_info = predictor(self.frame[:, :, ::-1])["panoptic_seg"]

        outputs = predictor(self.frame)

        return outputs, panoptic_seg, segments_info

    def __visualize(self,outputs, panoptic_seg):
        v = Visualizer(self.frame[:, :, ::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), scale=1)
        out = v.draw_panoptic_seg_predictions(panoptic_seg.to("cpu"), self.segments_info)

        classes = outputs["instances"].pred_classes.tolist()

        return out, classes
