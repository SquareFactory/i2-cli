"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import asyncio
import socket
from contextlib import closing

import msgpack
import numpy as np
import pytest
import websockets

from i2_client import I2Client


def test_init():
    """Test archipel client initialization."""
    I2Client("", "")


def get_available_port() -> int:
    """Return an available port on host."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


async def close_all_tasks():
    """Close all asyncio running tasks."""
    for task in asyncio.all_tasks():
        task.cancel()
        try:
            # Wait until task is cancelled
            await task
        except (asyncio.exceptions.CancelledError, RuntimeError):
            pass


@pytest.fixture
def setup():
    """Setup for websocket serve."""
    host = "127.0.0.1"
    port = get_available_port()
    url = f"ws://{host}:{port}"
    return url, host, port


@pytest.mark.asyncio
async def test_archipel_client_connection_async_success(setup):
    """Test full connection and inference pipeline."""

    url, host, port = setup
    fake_data = np.random.randint(0, 255, (250, 250, 3), dtype=np.uint8)

    async def fake_user():
        await asyncio.sleep(0.1)
        async with I2Client(url, "good:access_key") as client:
            outputs = await client.async_inference(fake_data)
            assert len(outputs) == 1
            success, output = outputs[0]
            assert success
            assert np.equal(output, fake_data).all()

    async def fake_cld(websocket, path):
        recv = await websocket.recv()
        drecv = msgpack.unpackb(recv)
        data = {
            "input_type": "numpy.ndarray",
            "input_size": "variable",
            "output_type": "numpy.ndarray",
        }
        msg = msgpack.packb({"status": "success", "data": data})
        await websocket.send(msg)

        # received encoded data
        recv = await websocket.recv()
        drecv = msgpack.unpackb(recv)
        assert "data" in drecv

        msg = msgpack.packb({"status": "success", "data": drecv["data"]})
        await websocket.send(msg)

    start_server = websockets.serve(fake_cld, host, port)

    try:
        gather = asyncio.gather(fake_user(), start_server)
        await asyncio.wait_for(gather, timeout=5.0)

    finally:
        await close_all_tasks()


@pytest.mark.asyncio
async def test_client_connect_async_invalid_access(setup):
    """Test full connection and inference pipeline."""

    url, host, port = setup

    async def fake_user():
        await asyncio.sleep(0.1)
        with pytest.raises(ConnectionError):
            async with I2Client(url, "wrong:access_key"):
                pass

    async def fake_cld(websocket, path):
        recv = await websocket.recv()
        drecv = msgpack.unpackb(recv)
        assert "access_key" in drecv
        await websocket.send(msgpack.packb({"status": "fail", "message": "zbl"}))

    start_server = websockets.serve(fake_cld, host, port)

    try:
        gather = asyncio.gather(fake_user(), start_server)
        await asyncio.wait_for(gather, timeout=5.0)

    finally:
        await close_all_tasks()


@pytest.mark.asyncio
async def test_archipel_client_connection_async_fail_msgpack(setup):
    """Test full connection and inference pipeline."""

    url, host, port = setup

    async def fake_user():
        await asyncio.sleep(0.1)
        with pytest.raises(ValueError):
            async with I2Client(url, "good:access_key") as client:
                fake_data = np.random.randint(0, 255, (250, 250, 3))
                await client.async_inference(fake_data)

    async def fake_cld(websocket, path):
        await websocket.recv()
        data = {
            "input_type": "None",
            "input_size": "variable",
            "output_type": "None",
        }
        await websocket.send(msgpack.packb({"status": "success", "data": data}))

    start_server = websockets.serve(fake_cld, host, port)

    try:
        gather = asyncio.gather(fake_user(), start_server)
        await asyncio.wait_for(gather, timeout=5.0)

    finally:
        await close_all_tasks()


@pytest.mark.asyncio
async def test_archipel_client_connection_async_fail_to_encode(setup):
    """Test full connection and inference pipeline."""

    url, host, port = setup

    def raise_error(*args, **kwargs):
        raise TypeError()

    async def fake_user():
        await asyncio.sleep(0.1)
        with pytest.raises(ValueError):
            async with I2Client(url, "good:access_key") as client:
                fake_data = np.random.randint(0, 255, (250, 250, 3))
                await client.async_inference(fake_data, encode=raise_error)

    async def fake_cld(websocket, path):
        await websocket.recv()
        data = {
            "input_type": "zbl",
            "input_size": "variable",
            "output_type": "None",
        }
        await websocket.send(msgpack.packb({"status": "success", "data": data}))

    start_server = websockets.serve(fake_cld, host, port)

    try:
        gather = asyncio.gather(fake_user(), start_server)
        await asyncio.wait_for(gather, timeout=5.0)

    finally:
        await close_all_tasks()


@pytest.mark.asyncio
async def test_archipel_client_connection_async_got_invalid_message(setup):
    """Test full connection and inference pipeline."""

    url, host, port = setup

    async def fake_user():
        await asyncio.sleep(0.1)
        with pytest.raises(RuntimeError):
            async with I2Client(url, "good:access_key") as client:
                await client.async_inference("zbl")

    async def fake_cld(websocket, path):
        await websocket.recv()
        data = {
            "input_type": "None",
            "input_size": "variable",
            "output_type": "None",
        }
        await websocket.send(msgpack.packb({"status": "success", "data": data}))

        await websocket.recv()
        await websocket.send(msgpack.packb({"zbl": "success"}))

    start_server = websockets.serve(fake_cld, host, port)

    try:
        gather = asyncio.gather(fake_user(), start_server)
        await asyncio.wait_for(gather, timeout=5.0)

    finally:
        await close_all_tasks()


@pytest.mark.asyncio
async def test_archipel_client_connection_async_got_inference_fail(setup, mocker):
    """Test full connection and inference pipeline."""

    url, host, port = setup

    fake_msg = "zbl"

    async def fake_user():
        await asyncio.sleep(0.1)
        async with I2Client(url, "good:access_key") as client:
            outputs = await client.async_inference("coucou")
            assert len(outputs) == 1
            success, output = outputs[0]
            assert not success
            assert output == fake_msg

    async def fake_cld(websocket, path):
        await websocket.recv()
        data = {
            "input_type": "None",
            "input_size": "variable",
            "output_type": "None",
        }
        await websocket.send(msgpack.packb({"status": "success", "data": data}))

        await websocket.recv()
        await websocket.send(msgpack.packb({"status": "fail", "message": fake_msg}))

    start_server = websockets.serve(fake_cld, host, port)

    try:
        gather = asyncio.gather(fake_user(), start_server)
        await asyncio.wait_for(gather, timeout=5.0)

    finally:
        await close_all_tasks()
