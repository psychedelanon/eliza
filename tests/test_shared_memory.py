import asyncio
import os
import sys
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eliza import shared_memory


@pytest.mark.asyncio
async def test_read_write():
    await shared_memory.write("key", 1)
    assert await shared_memory.read("key") == 1


@pytest.mark.asyncio
async def test_append_concurrency():
    async def worker(i):
        await shared_memory.append_list("list", i, maxlen=5)

    await asyncio.gather(*(worker(i) for i in range(10)))
    data = await shared_memory.read("list")
    assert len(data) == 5
    assert data[-1] == 9


@pytest.mark.asyncio
async def test_latest_default():
    assert await shared_memory.latest("missing", default="x") == "x"
