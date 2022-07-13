# Getting started

## Command line

### Inference

Inference means sending data to a model and getting a response,which is the simplest use for the client. We implemented a simple example, which makes use of the client to stream your webcam to a model on isquare. it can be used:

```
cd examples

# Stream your webcam
python webcam_stream.py \
  --url wss://archipel-beta1.isquare.ai/43465956-8d6f-492f-ad45-91da69da44d0 \
  --access_uuid access:48c1d60a-60fd-4643-90e4-cd0187b4fd9d
```
In the same spirit, we encourage you to write scripts implementing isquare models in your own application!

### Testing

The client allows you to build and test your model before uploading it to isquare.ai. We encourage 
you to test this feature, which we are sure will save you alot of time. For instance, try running:

```bash
i2py build examples/tasks/mirror.py --cpu
```
You should see following output:

```bash
[15:47:44] INFO     Building task from 'examples/tasks/mirror.py'...
[15:47:44] INFO     No Dockerfile found, use CPU base image
[15:47:44] INFO     Building 'i2-task-mirror:latest'...
[15:47:45] INFO     [DOCKER SDK LOG] Step 1/2 : FROM alpineintuition/archipel-base-cpu
[15:47:45] INFO     [DOCKER SDK LOG]  ---> e45cbd84d372
[15:47:45] INFO     [DOCKER SDK LOG] Step 2/2 : COPY examples/tasks/mirror.py /opt/archipel/worker_script.py
[15:47:45] INFO     [DOCKER SDK LOG]  ---> Using cache
[15:47:45] INFO     [DOCKER SDK LOG]  ---> cf0f4cf35f32
[15:47:45] INFO     [DOCKER SDK LOG] Successfully built cf0f4cf35f32
[15:47:45] INFO     [DOCKER SDK LOG] Successfully tagged i2-task-mirror:latest
[15:47:45] INFO     Building ended successfully!
[15:47:45] INFO     Testing...
[15:47:46] INFO     Testing ended successfully!
[15:47:46] INFO     Building and testing done! (docker tag: 'i2-task-mirror:latest')
```

Indicating that the test was successfull.

> **TIPS**: You can add build argument, like in docker, with the argument `--build-args`. You 
can use it multiple times to add multiples argument. Example: `--build-args ENV=VALUE`

## Integrate on code

The client can easily be integrated with existing code:

```
from i2_client import I2Client

client = I2Client("wss://archipel-beta1.isquare.ai/<TASK>", <ACCESS_KEY>)
outputs = client.inference(inputs)

```

More examples on [examples folder](/examples).
