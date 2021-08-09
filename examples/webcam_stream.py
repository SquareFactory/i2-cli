"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import argparse
import asyncio
import time

import cv2
import numpy as np

from i2_client import I2Client

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="", required=True)
parser.add_argument("--access_uuid", type=str, help="", required=True)
parser.add_argument("--frame_rate", type=int, help="", default=15)
args = parser.parse_args()


async def main():
    """Main async function."""

    cam = cv2.VideoCapture(0)
    prev = 0

    async with I2Client(args.url, args.access_uuid) as client:
        while True:
            time_elapsed = time.time() - prev
            check, frame = cam.read()
            if time_elapsed < 1.0 / args.frame_rate:
                # force the webcam frame rate so the bottleneck is the
                # inference, not the camera performance.
                continue
            prev = time.time()

            print("send...", end=" ")

            start = time.time()
            outputs = await client.async_inference(frame)
            end = time.time()

            print(f"got! in {end - start:.4f} secs (send + inference + receive)")

            concatenate_imgs = np.concatenate((frame, outputs[0]), axis=1)
            cv2.imshow("original / inference ", concatenate_imgs)

            key = cv2.waitKey(1)
            if key == 27:
                break

        cam.release()
        cv2.destroyAllWindows()


asyncio.run(main())
