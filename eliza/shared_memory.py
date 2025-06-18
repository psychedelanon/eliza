import asyncio
from typing import Any, Dict, List

_store: Dict[str, Any] = {}
_lock = asyncio.Lock()

async def read(key: str) -> Any:
    async with _lock:
        return _store.get(key)

async def write(key: str, value: Any) -> None:
    async with _lock:
        _store[key] = value

async def append_list(key: str, value: Any, maxlen: int = 25) -> None:
    async with _lock:
        lst: List[Any] = _store.get(key, [])
        lst.append(value)
        if len(lst) > maxlen:
            lst = lst[-maxlen:]
        _store[key] = lst

async def latest(key: str, default: Any = None) -> Any:
    async with _lock:
        lst = _store.get(key, [])
        if isinstance(lst, list) and lst:
            return lst[-1]
        return default
