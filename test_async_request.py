import asyncio
import time
import psycopg2
import psycopg

async def counter():
    now = time.time()
    print("Started counter")
    for i in range(0, 10):
        last = now
        await asyncio.sleep(0.001)
        now = time.time()
        print(f"{i}: Was asleep for {now - last}s")

async def main():
    t = asyncio.get_event_loop().create_task(counter())

    await asyncio.sleep(0)

    print("Sending HTTP request")
    # r = requests.get('http://example.com')
    dsn = "host=0.0.0.0 port=5432 dbname=tracer user=postgres password=mysecretpassword"
    # conn = psycopg2.connect(dsn, None, None)
    # conn = psycopg.connect(dsn)
    aconn = await psycopg.AsyncConnection.connect(dsn)
    print(f"Got HTTP response with status {aconn}")

    await t

asyncio.get_event_loop().run_until_complete(main())
