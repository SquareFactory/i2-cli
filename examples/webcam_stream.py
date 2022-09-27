"""Copyright (C) Square Factory SA - All Rights Reserved.

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
import imutils
import numpy as np
from rich.live import Live
from rich.spinner import Spinner

from i2_client import I2Client

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="", required=True)
parser.add_argument("--access_uuid", type=str, help="", required=True)
parser.add_argument("--frame_rate", type=int, help="", default=15)
parser.add_argument("--resize_width", type=int, help="", default=None)
args = parser.parse_args()


async def main():
    """Main async function."""

    cam = cv2.VideoCapture(0)
    prev = 0

    async with I2Client(args.url, args.access_uuid) as client:

        spinner = Spinner("dots2", "connecting...")
        with Live(spinner, refresh_per_second=20):

            durations = []

            while True:

                # 1. get webcam frame

                time_elapsed = time.time() - prev
                check, frame = cam.read()
                if time_elapsed < 1.0 / args.frame_rate:
                    # force the webcam frame rate so the bottleneck is the
                    # inference, not the camera performance.
                    continue
                prev = time.time()

                if args.resize_width is not None:
                    frame = imutils.resize(frame, width=args.resize_width)

                # 2. inference

                start = time.time()
                outputs = await client.async_inference(frame)
                durations.append(time.time() - start)

                # 3. show

                spinner.text = (
                    f"send + infer + receive: {durations[-1]:.4f} secs "
                    + f"(mean: {np.mean(durations):.4f}, std: {np.std(durations):.4f}, "
                    + f"min: {np.min(durations):.4f}, max: {np.max(durations):.4f})"
                )

                success, output = outputs[0]
                if not success:
                    raise RuntimeError(output)
                h, w, _ = frame.shape
                frame = cv2.resize(frame, (w * 2, h * 2))
                output = cv2.resize(output, (w * 2, h * 2))
                concatenate_imgs = np.concatenate((frame, output), axis=1)
                cv2.imshow("original / inference ", concatenate_imgs)
                key = cv2.waitKey(1)
                if key == 27:
                    break

        cam.release()
        cv2.destroyAllWindows()


asyncio.run(main())
