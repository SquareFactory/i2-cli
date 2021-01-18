import argparse
import asyncio
import time

import cv2

from archipel_client import ArchipelClient


parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="", required=True)
parser.add_argument("--port", type=int, help="", required=True)
parser.add_argument(
    "--access_uuid",
    type=str,
    help="",
    default="access:472f9457-072c-4a1a-800b-75ecdd6041e1",
)
args = parser.parse_args()

url = f"ws://{args.url}:{args.port}"


async def main():
    cam = cv2.VideoCapture(0)

    async with ArchipelClient(url, args.access_uuid) as ws:
        while True:
            check, frame = cam.read()

            start = time.time()
            outputs = await ws.async_inference(frame)
            end = time.time()

            print(f"duration: {end - start:.4f} ms (send + inference + receive)")

            cv2.imshow("1", frame)
            cv2.imshow("2", outputs[0])

            key = cv2.waitKey(1)
            if key == 27:
                break

        cam.release()
        cv2.destroyAllWindows()


asyncio.run(main())
