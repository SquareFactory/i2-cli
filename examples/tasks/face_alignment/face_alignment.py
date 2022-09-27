"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import sys

import cv2
from archipel.workers.worker import ImagesToDictsWorker

sys.path.append("/opt/3ddfa")
from FaceBoxes.FaceBoxes_ONNX import FaceBoxes_ONNX as FaceBoxes  # noqa
from TDDFA_ONNX import TDDFA_ONNX as TDDFA  # noqa
from utils.functions import cv_draw_landmark  # noqa
from utils.render_ctypes import render  # noqa

__task_class_name__ = "FaceAlignementWorker"


class FaceAlignementWorker(ImagesToDictsWorker):
    """Apply  detector worker for Coco dataset."""

    def setup_model(self):
        self.face_detector = FaceBoxes()

        cfg = {
            "arch": "mobilenet",
            "widen_factor": 1.0,
            "checkpoint_fp": "/opt/3ddfa/weights/mb1_120x120.pth",
            "bfm_fp": "/opt/3ddfa/configs/bfm_noneck_v3.pkl",
            "size": 120,
            "num_params": 62,
        }
        self.tddfa = TDDFA(**cfg)

    def forward(self, imgs):
        outputs = []
        for img in imgs:
            faces = self.face_detector(img)
            params, roi_boxes = self.tddfa(img, faces)
            vertexes = self.tddfa.recon_vers(params, roi_boxes, dense_flag=False)
            outputs.append(vertexes)
        return outputs


if __name__ == "__main__":
    worker = FaceAlignementWorker()

    if worker.args.test_input:
        img = cv2.imread(worker.args.test_input)
        print(worker.forward([img])[0])
