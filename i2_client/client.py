"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import asyncio
import logging
from typing import Any, Callable, List, Tuple

import archipel_utils as utils
import msgpack
import websockets

log = logging.getLogger(__name__)


class I2Client:
    """A class to manage the connection to a worker and inferences."""

    def __init__(self, url: str, access_key: str, debug: bool = True):
        """Initialize the isquare client.

        Args:
            url: Url of the model to use (provided on isquare.ai).
            access_key: Access key for the model (generated on isquare.ai)
            debug: Optional; Show extensive logs.

        Returns:
            None.

        Raises:
            None.
        """

        self.url = url
        self.access_key = access_key

        if debug:
            log.setLevel(logging.DEBUG)

        encode_functions = {
            "dict": lambda x: x,
            "numpy.ndarray": utils.serialize_array,
        }
        decode_functions = {
            "dict": lambda x: x,
            "numpy.ndarray": utils.deserialize_array,
        }
        self.available_transforms = {
            "encode": encode_functions,
            "decode": decode_functions,
        }

    async def __aenter__(self):
        """Async context manager enter, including archipel connection.

        Args:
            None.

        Returns:
            The client, connected to archipel with the given info.

        Raises:
            ConnectionError: There's a problem connecting to archipel with
                the specified url/access key pair.
        """

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

            if value == "None" or value is None:
                log.info(f"{key}: built-in")
            elif value in self.available_transforms[arg]:
                log.info(f"{key}: {value}")
                self.transforms[arg] = self.available_transforms[arg][value]
            else:
                log.warning(
                    f"Unknown {key} provided by task ({key}). You must provide "
                    + f"one to the inference function with the '{arg}' argument."
                )

        return self

    async def __aexit__(self, *args, **kwargs):
        """Async context manager exit.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        await self._conn.__aexit__(*args, **kwargs)

    async def async_inference(
        self, inputs: Any, encode: Callable = None, decode: Callable = None
    ) -> List[Tuple[bool, Any]]:
        """Send inference to archipel in async way.

        Args:
            inputs: The inputs to send to the worker.
            encode: Optional; Specify a specific input encoding.
            decode: Optional; Specify a specific output decoding.

        Returns:
            List of Tuple composed of two values: bool to indicate whether inference
            is a success and the inference is success or an error message if fail.

        Raises:
            ValueError: There was an error encoding or packing the given
                input (the specific error is printed).
            RuntimeError: Ther was an error during the inference (the
                specific error message is printed).
        """

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
            success, error_msg, decoded_msg = utils.get_decoded_msg(msg, {"status"})
            if not success:
                raise RuntimeError(error_msg)

            if decoded_msg["status"] == "success":
                inference = decoded_msg["data"]
                if decode is not None:
                    inference = decode(inference)
                outputs.append((True, inference))
            else:
                outputs.append((False, decoded_msg["message"]))

        return outputs

    def inference(
        self, inputs: Any, encode: Callable = None, decode: Callable = None
    ) -> List[Tuple[bool, Any]]:
        """Send inference to archipel in sync way.

        Args:
            inputs: The inputs to send to the worker.
            encode: Optional; Specify a specific input encoding.
            decode: Optional; Specify a specific output decoding.

        Returns:
            List of Tuple composed of two values: bool to indicate whether inference
            is a success and the inference is success or an error message if fail.

        Raises:
            None.
        """

        async def _inference(self, inputs):
            await self.__aenter__()
            outputs = await self.async_inference(inputs, encode, decode)
            await self.__aexit__(exc_type=None, exc_value=None, traceback=None)
            return outputs

        return asyncio.run(_inference(self, inputs))
