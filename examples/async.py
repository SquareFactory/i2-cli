import asyncio
import time

import cv2

from archipel_client import ArchipelClient


url = "ws://127.0.0.1:9001"
access_uuid = "access:472f9457-072c-4a1a-800b-75ecdd6041e1"
# TODO REMOVE


async def main():
    cam = cv2.VideoCapture(0)

    async with ArchipelClient(url, access_uuid) as ws:
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
