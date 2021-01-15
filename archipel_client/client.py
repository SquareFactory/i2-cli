import asyncio

import msgpack
import websockets

from .utils import img_to_binary, binary_to_img


class ArchipelClient:
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

    async def async_inference(self, imgs):
        if not isinstance(imgs, list):
            imgs = [imgs]

        outputs = []
        for img in imgs:
            binary_img = img_to_binary(img)
            extra_data = ""
            await self.websocket.send(msgpack.packb([binary_img, extra_data]))
            binary_outputs = await self.websocket.recv()
            outputs.append(binary_to_img(binary_outputs))

        return outputs

    def inference(self, imgs):
        async def _inference(self, imgs):
            await self.__aenter__()
            outputs = await self.async_inference(imgs)
            await self.__aexit__(exc_type=None, exc_value=None, traceback=None)
            return outputs

        return asyncio.run(_inference(self, imgs))
