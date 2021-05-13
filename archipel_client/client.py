import asyncio

import msgpack
import websockets

from .utils import binary_to_img, img_to_binary


class ArchipelClient:
    """A class to manage the connection to a worker."""

    def __init__(self, url: str, access_uuid: str):
        self.url = url
        self.access_uuid = access_uuid.encode()
        self.websocket = None

    async def __aenter__(self):
        self._conn = websockets.connect(self.url)
        self.websocket = await self._conn.__aenter__()

        await self.websocket.send(self.access_uuid)
        response = await self.websocket.recv()
        if response.decode() != "connected":
            raise ConnectionError("Unauthorized or invalid access uuid")

        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    def check_inputs(self, inputs):
        # To adapt depending the input and the output
        raise NotImplementedError

    def check_outputs(self, outputs):
        # To adapt depending the input and the output
        raise NotImplementedError

    async def async_inference(self, inputs):
        inputs = self.check_inputs(inputs)

        outputs = []
        for input in inputs:
            extra_data = ""
            await self.websocket.send(msgpack.packb([input, extra_data]))
            output = await self.websocket.recv()
            outputs.append(output)
        outputs = self.check_outputs(outputs)

        return outputs

    def inference(self, inputs):
        async def _inference(self, inputs):
            await self.__aenter__()
            outputs = await self.async_inference(inputs)
            await self.__aexit__(exc_type=None, exc_value=None, traceback=None)
            return outputs

        return asyncio.run(_inference(self, inputs))


class ArchipelVisionClient(ArchipelClient):
    """Vision Client."""

    def check_inputs(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]
        return [img_to_binary(img).decode() for img in inputs]

    def check_outputs(self, outputs):
        outputs = [binary_to_img(output) for output in outputs]
        # TODO adapt for other outputs
        return outputs
