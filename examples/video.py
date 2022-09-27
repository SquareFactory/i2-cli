"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import argparse
import asyncio
from pathlib import Path

import cv2

from i2_client import I2Client

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="", required=True)
parser.add_argument("--access_uuid", type=str, help="", required=True)
parser.add_argument("--video_path", type=str, help="", required=True)
parser.add_argument("--save_path", type=str, help="", default=None)
args = parser.parse_args()

# Check arguments

path = Path(args.video_path)
if not path.is_file():
    raise FileNotFoundError(f"No file at {path}")

valid_suffixes = [".mp4"]
if path.suffix not in valid_suffixes:
    raise TypeError(
        "The video has an suffix. Valid suffixes: {' ,'.join(valid_suffixes)}"
    )

if args.save_path is None:
    save_path = path.parent / f"{path.stem}_processed.mp4"
else:
    save_path = Path(args.save)
    if save_path.is_file():
        raise FileExistsError("The save path is already exist")

# Main function


async def main():
    """Main async function."""

    async with I2Client(args.url, args.access_uuid) as client:
        # Start video reader
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise ValueError("Error opening video")

        # Make the first inference to get inference output size
        ok, frame = cap.read()
        if not ok:
            raise ValueError("Error reading video")

        outputs = await client.async_inference(frame)

        # Start video writer
        fourcc = cv2.VideoWriter_fourcc(*"MP4V")
        fps = 25
        output_shape = (outputs[0].shape[0], outputs[0].shape[1])
        out = cv2.VideoWriter(str(save_path), fourcc, fps, output_shape)

        out.write(outputs[0])
        count = 1

        # Inference until video is completly processed
        while True:
            ok, frame = cap.read()
            if not ok:
                # End of the video
                break

            outputs = await client.async_inference(frame)

            success, output = outputs[0]
            if not success:
                raise RuntimeError(output)
            out.write(output)

            count += 1
            if not bool(count % 25):
                print(f"processed {count} frames")

        # Release reader and writer
        cap.release()
        out.release()

        print(f"processed video saved at: {save_path}")


asyncio.run(main())
