import time

import cv2

from archipel_client import ArchipelClient

url = "ws://127.0.0.1:9001"
access_uuid = "access:472f9457-072c-4a1a-800b-75ecdd6041e1"
# TODO REMOVE


archipel_client = ArchipelClient(url, access_uuid)

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
