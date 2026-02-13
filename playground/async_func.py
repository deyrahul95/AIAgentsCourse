import random
import asyncio


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
    await do_something()
    await do_something_more()


if __name__ == "__main__":
    asyncio.run(main=main())
