import argparse
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

# url = f"wss://{args.url}:{args.port}"
url = "wss://arch2.isquare.ai/pixelizer"
archipel_client = ArchipelClient(url, args.access_uuid)

img = cv2.imread("test.jpg")
if img is None:
    raise FileNotFoundError("invalid image")

start = time.time()
output = archipel_client.inference(img)[0]
end = time.time()

print(f"duration: {end - start:.4f} ms (open connection + send + inference + receive)")
print("press on any key to quit...")

cv2.imshow("original", img)
cv2.imshow("inference", output)
cv2.waitKey(0)
cv2.destroyAllWindows()
