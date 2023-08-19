import asyncio

from dotenv import load_dotenv

from start_quests import start_quests
import time
from finish_quests import finish_quests

load_dotenv()

async def start():
    while True:
        start_quests()
        await asyncio.sleep(300)

async def finish():
    while True:
        try:
            finish_quests("CRYSTALVALE")
        except:
            continue
        await asyncio.sleep(300)

async def async_main():
    res = await asyncio.gather(start(), finish())
    return res

def main():
    print('HELLO WORLD!')
    res = asyncio.run(async_main())
    print(f"in main, result is {res}")

if __name__ == "__main__":
    main()