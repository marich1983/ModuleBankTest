import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="operation_db",
        host="localhost",
        port=5432,
    )

    print("connected")

    await conn.close()


asyncio.run(main())