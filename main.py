from logging import basicConfig, INFO
from asyncio import run
from bot import bot, dp


async def main():
    await dp.start_polling(bot)


if __name__ =="__main__":
    while True:
        try:
            basicConfig(level=INFO)
            run(main())
        except:
            continue
