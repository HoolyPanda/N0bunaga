import asyncio
import time

# @asyncio.coroutine
a = [1]
async def test1():
    while True:
        print('test1')
        i +=1


async def test2():
    print('test2')

async def main():
    test1()
    test2()

loop = asyncio.new_event_loop()
loop.run_until_complete(asyncio.gather(
    test1(),
    test2()
))
loop.close()