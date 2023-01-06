"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import argparse
import asyncio
import multiprocessing
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
parser.add_argument("--inference_time", type=int, default=20)
parser.add_argument(
    "--num_clients", help="number of simultaneous clients", type=int, default=50
)
parser.add_argument("--asyncio", help="launch using asyncio.", action="store_true")
args = parser.parse_args()


async def single_stream_async(path="examples/test.jpg"):
    """Continuously stream single image in async fashion."""
    t0 = time.time()
    img = cv2.imread(path)
    prev = 0
    async with I2Client(args.url, args.access_uuid) as client:

        spinner = Spinner("dots2", "connecting...")
        with Live(spinner, refresh_per_second=20):

            durations = []

            while True:

                # 1. get webcam frame

                time_elapsed = time.time() - prev

                if time_elapsed < 1.0 / args.frame_rate:
                    # force the webcam frame rate so the bottleneck is the
                    # inference, not the camera performance.
                    continue
                prev = time.time()

                if args.resize_width is not None:
                    img = imutils.resize(img, width=args.resize_width)

                # 2. inference

                start = time.time()
                outputs = await client.async_inference(img)
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
                key = cv2.waitKey(1)
                if key == 27:
                    break
                if time.time() - t0 > args.inference_time:
                    break


# asyncio.run(single_stream())


def single_stream(path="examples/test.jpg"):
    """Continuously stream single image."""
    t0 = time.time()
    img = cv2.imread(path)
    prev = 0
    client = I2Client(args.url, args.access_uuid)
    durations = []
    while True:
        time_elapsed = time.time() - prev
        if time_elapsed < 1.0 / args.frame_rate:
            # force the webcam frame rate so the bottleneck is the
            # inference, not the camera performance.
            continue
        prev = time.time()
        if args.resize_width is not None:
            img = imutils.resize(img, width=args.resize_width)
        start = time.time()
        success, output = client.inference(img)[0]
        durations.append(time.time() - start)
        if not success:
            raise RuntimeError(output)
        key = cv2.waitKey(1)
        if key == 27:
            print(
                f"(mean: {np.mean(durations):.4f}, std: {np.std(durations):.4f}, "
                + f"min: {np.min(durations):.4f}, max: {np.max(durations):.4f})"
            )
            break
        if time.time() - t0 > args.inference_time:
            print(
                f"(mean: {np.mean(durations):.4f}, std: {np.std(durations):.4f}, "
                + f"min: {np.min(durations):.4f}, max: {np.max(durations):.4f})"
            )
            break


async def multi_stream_async():
    """Asynchronously stream images."""

    tasks = []
    print(f"Launching {args.num_clients} parallel clients")
    for i in range(args.num_clients):
        task = asyncio.ensure_future(single_stream_async())
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)


def multi_stream_mp():
    """Stream images in true parallel fashion."""
    paths = args.num_clients * ["examples/test.jpg"]
    with multiprocessing.Pool() as pool:
        pool.map(single_stream, paths)


if args.asyncio:
    asyncio.get_event_loop().run_until_complete(multi_stream_async())
else:
    multi_stream_mp()
