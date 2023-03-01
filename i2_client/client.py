"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import asyncio
import logging
from typing import Any, Callable, List, Optional, Tuple

import archipel_utils as utils
import msgpack
import websockets
from rich.logging import RichHandler

log = logging.getLogger(__name__)


class I2Client:
    """A class to manage the connection to a worker and inferences."""

    def __init__(self, url: str, access_key: str, debug: bool = False):
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

        handlers = [
            RichHandler(
                show_path=False,
                omit_repeated_times=False,
                log_time_format="[%H:%M:%S]",
                markup=True,
            )
        ]

        logging.basicConfig(
            format="%(message)s",
            level=logging.DEBUG if debug else logging.WARN,
            handlers=handlers,
        )

        logging.getLogger("websockets").propagate = False

        self.transforms = {
            "encode": {
                "ndarray": utils.serialize_array,
            },
            "decode": {
                "ndarray": utils.deserialize_array,
            },
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

        self._conn = websockets.connect(self.url, max_size=2**50)
        self.websocket = await self._conn.__aenter__()

        msg = {"action": "Registration", "data": self.access_key}

        msg["access_key"] = self.access_key
        # TODO: keep for backcomp, remove when possible

        await self.websocket.send(msgpack.packb(msg))
        log.debug("Registration sended, wait for response")

        msg = await self.websocket.recv()
        decoded_msg = msgpack.unpackb(msg, strict_map_key=False)

        if decoded_msg["status"].lower() != "success":
            raise ConnectionError(
                f"Can not connect to Archipel: {decoded_msg['message']}"
            )

        if "data" in decoded_msg:
            input_type = decoded_msg["data"]["input_type"]
            input_type = input_type.replace("numpy.", "")
            output_type = decoded_msg["data"]["output_type"]
            output_type = output_type.replace("numpy.", "")
            # TODO remove when archipel rust version is used everywhere
        elif "workload_typing" in decoded_msg:
            input_type = decoded_msg["workload_typing"]["input"]
            output_type = decoded_msg["workload_typing"]["output"]
        else:
            raise ValueError("Missing types in archipel response")

        self.encode = self.transforms["encode"].get(input_type, lambda x: x)
        self.decode = self.transforms["decode"].get(output_type, lambda x: x)

        log.info(
            "Successfully connected to archipel! "
            + f"input_type={input_type}, output_type={output_type})"
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
        self,
        inputs: Any,
        encode: Optional[Callable] = None,
        decode: Optional[Callable] = None,
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

        encode = self.encode if encode is None else encode
        decode = self.decode if decode is None else decode

        outputs = []
        for inp in inputs:
            try:
                inp = encode(inp)
            except Exception as error:
                ValueError(f"Fail to encode input: {error}")

            try:
                msg = msgpack.packb({"action": "Inference", "data": inp})
            except Exception as error:
                raise ValueError(f"Fail to msgpack input: {error}")

            await self.websocket.send(msg)
            log.debug("Data sended, wait for response")

            msg = await self.websocket.recv()
            decoded_msg = msgpack.unpackb(msg, strict_map_key=False)

            keys = set(decoded_msg.keys())
            valid = keys.issubset(["status", "message", "data"])
            backcomp_valid = keys.issubset(["status", "action", "message", "data"])
            if not valid and not backcomp_valid:
                raise ValueError("Invalid message received, missing fields")
            log.debug("Got an valid response")

            if decoded_msg["status"].lower() == "success":
                try:
                    inference = decode(decoded_msg["data"])
                    outputs.append((True, inference))
                except Exception as error:
                    outputs.append((False, f"Fail to decode output: {error}"))
            else:
                outputs.append((False, decoded_msg["message"]))

        return outputs

    def inference(
        self,
        inputs: Any,
        encode: Optional[Callable] = None,
        decode: Optional[Callable] = None,
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
