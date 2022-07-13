# Examples 
This directory shows 3 sample integrations of the [ISquare](http://isquare.ai) client for image inference, with 3 levels of complexity:
- How to perform inference with an image
- How to perform inference with a video
- How to stream a camera to your model

## Simple inference
First, we'll look at how to perform a simple inference with an image file. To start, we need to import our libraries and initialize the client:
```python
from i2_client import I2Client
import cv2
import numpy as np

# You need your url, access key and an image
url = "wss://archipel-beta1.isquare.ai/43465956-8d6f-492f-ad45-91da69da44d0"
access_key = "472f9457-072c-4a1a-800b-75ecdd6041e1"

inference_client = I2Client(url,access_key)

```
Then, we load the image using OpenCV and verify it is loaded correctly
```python
img = cv2.imread("test.jpg")
if img is None:
    raise FileNotFoundError("invalid image")
```
Finally, we just have to call our model using the client. If using an image to image model, we can show the original and the saved image next to each other:
```python
success, output = inference_client.inference(img)[0]
concatenate_imgs = np.concatenate((img, output), axis=1)
cv2.imshow("original / inference ", concatenate_imgs)
```
And that's it for the simple usage of the client. Our client currently supports strings, numpy arrays, and any python dictionary objects, as long as they are numpy serialisable. If you have a sentiment analysis model for text, your inference could look like the following:

```python

success, output = inference_client.inference("It's a rainy summer day")
```
or, for a dictionary:
```python

success, output = inference_client.inference({"key":value})
```

## Async example
As inference might take a couple of seconds to process (mostly depending on your model), you might want to call your model in an async way. To show how to do that, we will write a client which streams your primary webcam to your model.

We first capture the camera output using OpenCV, and then send the data to the model at a certain framerate:
```python
url = "wss://archipel-beta1.isquare.ai/43465956-8d6f-492f-ad45-91da69da44d0"
access_key = "472f9457-072c-4a1a-800b-75ecdd6041e1"
frame_rate = 15

async def main():
    """Stream a webcam to the model."""
    cam = cv2.VideoCapture(0)
    prev = 0

    async with I2Client(url, access_uuid) as client:
        while True:

            time_elapsed = time.time() - prev
            check, frame = cam.read() # read the cam
            if time_elapsed < 1.0 / args.frame_rate:
                # force the webcam frame rate so the bottleneck is the
                # inference, not the camera performance.
                continue
            prev = time.time()
            outputs = await client.async_inference(frame)
            success, output = outputs[0]

            if not success:
                raise RuntimeError(output)

            # showing original and inference for image to image model
            concatenate_imgs = np.concatenate((frame, outputs[0]), axis=1)
            cv2.imshow("original / inference ", concatenate_imgs)
        
        cam.release()
        cv2.destroyAllWindows()
asyncio.run(main())

```
You can easily stream any source to your model using this type of integration, as well as seemingly integrate your models in an async way, so that your code is completely independent of your model inference time.
