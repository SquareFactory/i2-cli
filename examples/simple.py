"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import argparse
import time
import warnings

import cv2
import numpy as np

from i2_client import I2Client

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, required=True)
parser.add_argument(
    "--access_uuid",
    type=str,
)
parser.add_argument(
    "--access-key",
    type=str,
)
parser.add_argument(
    "--debug",
    action="store_true",
)
args = parser.parse_args()

if args.access_uuid is not None:
    warnings.warn("--access_uuid is deprecated, use --access-key", DeprecationWarning)
    args.access_key = args.access_uuid
if args.access_uuid is None and args.access_key is None:
    raise ValueError("You have to provide an access key with --access-key")

i2_client = I2Client(args.url, args.access_key, debug=args.debug)

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
