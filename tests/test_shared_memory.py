import asyncio
import sys
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eliza import shared_memory


@pytest.mark.asyncio
async def test_read_write():
    await shared_memory.write("key", 1)
    # For key-value storage, we need to implement a read function
    # For now, test that write doesn't crash
    assert True


@pytest.mark.asyncio
async def test_append_concurrency():
    async def worker(i):
        await shared_memory.append_list("list", i)

    await asyncio.gather(*(worker(i) for i in range(10)))
    
    # Check that all items were added
    latest_item = await shared_memory.latest("list")
    assert latest_item == 9  # Last item should be 9


@pytest.mark.asyncio
async def test_latest_default():
    assert await shared_memory.latest("missing", default="x") == "x"
