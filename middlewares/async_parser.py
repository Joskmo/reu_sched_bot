from tokenize import group
import aiohttp
import asyncio

async def main():
    group_dict: dict = {
        'selection': "15.27д-би20/22б"
    }
    link = "http://rasp.rea.ru/Schedule/ScheduleCard"
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=link, headers=headers, params=group_dict) as resp:
            print(resp.status)
            print(await resp.text())
            print(resp.url)

asyncio.run(main())