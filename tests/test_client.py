"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import asyncio
from contextlib import closing
import socket

import numpy as np
import msgpack
import pytest
import websockets

from archipel_client import ArchipelClient


def test_init():
    """Test archipel client initialization."""
    ArchipelClient("", "")


def test_serialize_deserialize_np_array(mocker):
    """Test np serialization deserialization function."""

    client = ArchipelClient("", "")
    fake_data = np.random.randint(0, 255, (600, 600, 3))

    serialized = client._serialize_np_array(fake_data)
    deserialized = client._deserialize_np_array(serialized)
    assert np.equal(fake_data, deserialized).all()

    mocker.patch("cv2.imencode", return_value=(False, None))
    with pytest.raises(ValueError):
        client._serialize_np_array(fake_data)

    mocker.patch("cv2.imdecode", return_value=None)
    with pytest.raises(ValueError):
        client._deserialize_np_array(serialized)


@pytest.mark.parametrize(
    "data",
    [{"status": "success", "data": "zbl"}, {"status": "fail", "message": "zbl"}],
)
def test_valid_received_msg(data):
    """Test decoded message function."""
    client = ArchipelClient("", "")
    decoded_msg = client._get_decoded_msg(msgpack.packb(data))
    assert data == decoded_msg


@pytest.mark.parametrize(
    "msg",
    [
        "zbl",
        b"zbl",
        msgpack.packb({"zbl": "zbl"}),
        msgpack.packb({"status": "success"}),
        msgpack.packb({"status": "fail"}),
    ],
)
def test_invalid_received_msg(msg):
    """Test np serialization deserialization function."""
    client = ArchipelClient("", "")
    with pytest.raises(ValueError):
        client._get_decoded_msg(msg)


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
    fake_data = np.random.randint(0, 255, (250, 250, 3))

    async def fake_user():
        await asyncio.sleep(0.1)
        async with ArchipelClient(url, "good:access_key") as client:
            inference = await client.async_inference(fake_data)
            assert np.equal(inference, fake_data).all()

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
            async with ArchipelClient(url, "wrong:access_key"):
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
            async with ArchipelClient(url, "good:access_key") as client:
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
