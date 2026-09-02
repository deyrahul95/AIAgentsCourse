import asyncio
import random


async def do_something() -> str:
    """Wait for get the result and return"""
    delay = random.randint(5, 15)
    print(f"Pausing for {delay} seconds...")
    await asyncio.sleep(delay)
    print(f"Paused for {delay} seconds.")
    return "Done"


async def do_something_more() -> str:
    """Wait for get the result and return"""
    delay = random.randint(1, 5)
    print(f"Pausing for {delay} seconds...")
    await asyncio.sleep(delay)
    print(f"Paused for {delay} seconds.")
    return "Done"


async def main() -> None:
    results = await asyncio.gather(do_something(), do_something_more())
    print(results)


if __name__ == "__main__":
    asyncio.run(main=main())
