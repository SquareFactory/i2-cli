![Isquare deploy logo](docs/imgs/deploy_logo.png)
# Isquare client for Python

This repository contains the official python client for [ISquare](http://isquare.ai) deploy. It is available under the form of python classes which are ready to use in your code, as well as a command-line-interface. We currently support inference with image, text & json files, as well as any numpy array or python dictionnary or string, both for input and output. 

The complete documentation for ISquare can be found [here](http://docs.isquare.ai).

## Installation

### From pip

TODO when public.

### From source

```
pip install --editable .
```

### Additional requirements

To be able to test your model builds, you need the following packages:
Docker >= 19.03.13

_Note_: If you only need the client for inference, this is not required.

## Usage
The client can be used to verify your model build (e.g. checking if they will properly run on [ISquare](http://isquare.ai)) and to perform inference calls to your deployed models. To use this client for inference, you need to have a model up and running on [ISquare](http://isquare.ai).

Commands and their usage are described [here](docs/commands.md).

End-to-end guidelines on the code adaptation required to deploy a model on isquare.ai can be found [here](docs/isquare_tutorial.md).

## Examples

### Command line interface

#### Test if your model repository is Isquare-compatible
To verify if your code will run smoothly on [ISquare](http://isquare.ai), you can perform a local build & unit test. This will build a container image with all your specific dependencies and perform an inference test. We've included an example of a simple computer vision model which returns the mirrored image it is given, and it can be tested by running:

```bash
 i2py build examples/tasks/mirror.py
```
When you deploy a model with [ISquare](http://isquare.ai), you will be provided a url for the model, and requested to create access keys. Using a valid url & access keys (the one displayed are an example), you can perform an inference with an Image model (e.g. the Mirror) and a `.png` image by running:


```bash
i2py infer \
  --url wss://archipel-beta1.isquare.ai/43465956-8d6f-492f-ad45-91da69da44d0 \
  --access_uuid 48c1d60a-60fd-4643-90e4-cd0187b4fd9d \
  examples/test.png
```
Other examples can be found [here](docs/getting_started.md).

### Using a model inside your python code
As you probably want to automate your model calls by integrating them directly into your code, we've provided you with several python classes you can directly use in your code. The main class to use for that is the `I2Client` class. A simple inference can be performed as follows:

```python
from i2_client import I2Client
import cv2

# You need your url, access key and an image
url = "wss://archipel-beta1.isquare.ai/43465956-8d6f-492f-ad45-91da69da44d0"
access_key = "472f9457-072c-4a1a-800b-75ecdd6041e1"
img = cv2.imread("test.jpg")

# Initialize the client & perform inference
inference_client = I2Client(url,access_key)
success, output = inference_client.inference(img)[0]
```

A more complex example, showing how to stream a camera to your model, can be found [here](examples/webcam_stream.py).

