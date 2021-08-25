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

The client allows you to test your model before uploading it to isquare.ai. We encourage you to test this feature, which we are sure will save you alot of time. For instance, try running:

```bash
i2 test worker examples/tasks/mirror.py
```
You should see following output:

```bash
14:51:29 - INFO - Building task 'mirror'...
14:51:29 - INFO - Docker image creation
14:51:29 - INFO - No Dockerfile in 'examples/tasks', use base image
100%|█████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 10485.76 steps/s]
14:51:31 - INFO - Task 'mirror' successfully built!
14:51:31 - INFO - Testing the worker
14:51:32 - INFO - Worker test successful!
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
