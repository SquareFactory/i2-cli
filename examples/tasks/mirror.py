"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import cv2
from archipel.workers import ImagesToImagesWorker

__task_class_name__ = "MirrorWorker"


class MirrorWorker(ImagesToImagesWorker):
    """vertical symmetry worker."""

    def setup_model(self):
        pass

    def forward(self, imgs, **kwargs):
        return [cv2.flip(img, 1) for img in imgs]
