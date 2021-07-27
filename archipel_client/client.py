"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import asyncio
import base64
import logging

import cv2
import msgpack
import numpy as np
import websockets


log = logging.getLogger(__name__)


class ArchipelClient:
    """A class to manage the connection to a worker."""

    def __init__(self, url: str, access_key: str, debug: bool = True):
        self.url = url
        self.access_key = access_key

        if debug:
            log.setLevel(logging.DEBUG)

        self.websocket = None

        encode_functions = {
            "numpy.ndarray": self._serialize_np_array,
        }
        decode_functions = {
            "numpy.ndarray": self._deserialize_np_array,
        }
        self.available_transforms = {
            "encode": encode_functions,
            "decode": decode_functions,
        }

    async def __aenter__(self):
        """Async context manager enter, including archipel connection."""
        self._conn = websockets.connect(self.url)
        self.websocket = await self._conn.__aenter__()

        msg = {"access_key": self.access_key}
        await self.websocket.send(msgpack.packb(msg))

        msg = await self.websocket.recv()
        decoded_msg = msgpack.unpackb(msg)

        if decoded_msg["status"] != "success":
            raise ConnectionError(
                f"Can not connect to Archipel: {decoded_msg['message']}"
            )

        log.info("Successfully connected to archipel!")

        types = {
            "input_type": decoded_msg["data"]["input_type"],
            "output_type": decoded_msg["data"]["output_type"],
        }

        self.transforms = {}
        for key, value in types.items():
            arg = "encode" if key == "input_type" else "decode"

            if value == "None":
                log.warning(
                    f"No {key} provided by task. You must provide one "
                    + f"to the inference function with the '{arg}' argument."
                )
            elif value not in self.available_transforms[arg]:
                log.warning(
                    f"Unknown {key} provided by task ({key}). You must provide "
                    + f"one to the inference function with the '{arg}' argument."
                )
            else:
                log.info(f"{key}: {value}")
                self.transforms[arg] = self.available_transforms[arg][value]

        return self

    async def __aexit__(self, *args, **kwargs):
        """Async context manager exit."""
        await self._conn.__aexit__(*args, **kwargs)

    def _serialize_np_array(self, array: np.ndarray) -> bytes:
        """Serialize a numpy array into bytes."""
        success, encoded_array = cv2.imencode(".png", array)
        if not success:
            raise ValueError("Fail to encode array")
        return base64.b64encode(encoded_array)

    def _deserialize_np_array(self, serialized_array: bytes) -> np.ndarray:
        """Serialize a bytes variable into numpy array."""
        decoded_array = base64.b64decode(serialized_array)
        decoded_array = np.frombuffer(decoded_array, np.uint8)
        decoded_array = cv2.imdecode(decoded_array, cv2.IMREAD_UNCHANGED)
        if decoded_array is None:
            raise ValueError("Fail to decode serialized array")
        return decoded_array

    def _get_decoded_msg(self, msg: bytes) -> dict:
        """Decode websocket message and check mandatory keys."""
        try:
            decoded_msg = msgpack.unpackb(msg)
        except TypeError:
            raise ValueError(
                f"Invalid message received, must be <class 'bytes'>, got {type(msg)}"
            )
        except msgpack.exceptions.ExtraData:
            raise ValueError("Invalid message received, must be msgpacked")

        if "status" not in decoded_msg:
            raise ValueError("Invalid message received, missing 'status' key")

        if decoded_msg["status"] == "success" and "data" not in decoded_msg:
            raise ValueError(
                "Invalid received message: when success, a 'data' key is needed"
            )
        if decoded_msg["status"] != "success" and "message" not in decoded_msg:
            raise ValueError(
                "Invalid received message: when not success, a 'message' key is needed"
            )

        return decoded_msg

    async def async_inference(self, inputs, encode=None, decode=None):
        """Send inference to archipel in async way."""
        if not isinstance(inputs, list):
            inputs = [inputs]

        if encode is None and "encode" in self.transforms:
            encode = self.transforms["encode"]
        if decode is None and "decode" in self.transforms:
            decode = self.transforms["decode"]

        outputs = []
        for inp in inputs:
            if encode is not None:
                try:
                    inp = encode(inp)
                except Exception as error:
                    raise ValueError(f"Fail to encode input: {error}")

            try:
                msg = msgpack.packb({"data": inp})
            except Exception as error:
                raise ValueError(f"Fail to msgpack input: {error}")

            await self.websocket.send(msg)

            msg = await self.websocket.recv()
            decoded_msg = self._get_decoded_msg(msg)

            if decoded_msg["status"] == "success":
                inference = decoded_msg["data"]
                if decode is not None:
                    inference = decode(inference)
                outputs.append(inference)
            else:
                outputs.append(decoded_msg["message"])

        return outputs

    def inference(self, inputs, encode=None, decode=None):
        """Send inference to archipel in sync way."""

        async def _inference(self, inputs):
            await self.__aenter__()
            outputs = await self.async_inference(inputs, encode, decode)
            await self.__aexit__(exc_type=None, exc_value=None, traceback=None)
            return outputs

        return asyncio.run(_inference(self, inputs))
