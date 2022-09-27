"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import argparse
import time

import cv2
import numpy as np

from i2_client import I2Client

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="", required=True)
parser.add_argument(
    "--access_uuid",
    type=str,
    help="",
    default="472f9457-072c-4a1a-800b-75ecdd6041e1",
)
args = parser.parse_args()

i2_client = I2Client(args.url, args.access_uuid)

img = cv2.imread("test.jpg")
if img is None:
    raise FileNotFoundError("invalid image")

start = time.time()
success, output = i2_client.inference(img)[0]
duration = time.time() - start

print(f"duration: {duration:.4f} secs (open connection + send + inference + receive)")

if not success:
    raise RuntimeError(output)

print("press on any key to quit...")
concatenate_imgs = np.concatenate((img, output), axis=1)
cv2.imshow("original / inference ", concatenate_imgs)
cv2.waitKey(0)
cv2.destroyAllWindows()
