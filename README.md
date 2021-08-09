# Isquare client for Python

This repository contains the client for [isquare](isquare.ai). It is available under the form of python classes, as well as a command-line-interface.

## Installation

### From pip

TODO when public

### From source

```
pip install --editable .
```

### Additional requirements

To be able to test your models, you need the following packages:
Docker >= 19.03.13

_Note_: If you only need the client for inference, this is not required.

## Usage

Commands and their usage are described [here](docs/commands.md).

## Examples

Simple inference:

```bash
i2 infer \
  --url wss://archipel-beta1.isquare.ai/43465956-8d6f-492f-ad45-91da69da44d0 \
  --access_uuid access:48c1d60a-60fd-4643-90e4-cd0187b4fd9d \
  examples/test.png
```
Other examples can be found [here](docs/getting_started.md).
