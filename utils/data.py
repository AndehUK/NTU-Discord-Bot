import json
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union


async def get_rules(loop: AbstractEventLoop) -> List[str]:
    def parse_rules():
        with open("data/rules.txt", "r", encoding="utf-8") as f:
            return [l for l in f.readlines() if l.strip()]

    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, parse_rules)


async def get_message_data(loop: AbstractEventLoop, key: Optional[str] = None) -> Any:
    def parse_data() -> Any:
        with open("data/messages.json", "r") as f:
            data = json.load(f)
            return data.get(key) if key else data

    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, parse_data)


async def set_message_data(
    loop: AbstractEventLoop, key: str, value: Union[str, int]
) -> None:
    def set_data(key: str, value: Union[str, int]) -> Any:
        data: Dict[str, Union[str, int]] = {}

        with open("data/messages.json", "r+") as f:
            data = json.load(f)

            data[key] = value
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, set_data, key, value)
