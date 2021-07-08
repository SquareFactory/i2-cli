import asyncio

import json
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

    def encode(self, inp):
        # To adapt depending the input and the output
        raise NotImplementedError

    def decode(self, out):
        # To adapt depending the input and the output
        raise NotImplementedError

    async def async_inference(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]

        outputs = []
        for inp in inputs:
            encoded_inp = self.encode(inp)
            extra_data = ""

            await self.websocket.send(msgpack.packb([encoded_inp, extra_data]))

            out = await self.websocket.recv()

            if isinstance(out, str):
                outputs.append(out)
            else:
                outputs.append(self.decode(out))

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

    def encode(self, img):
        return img_to_binary(img).decode()

    def decode(self, binary_img):
        return binary_to_img(binary_img.decode())


class ArchipelDictsClient(ArchipelClient):
    """Dictionnary Client."""

    def encode(self, inp):
        return json.dumps(inp)

    def decode(self, inp):
        return json.loads(inp)
