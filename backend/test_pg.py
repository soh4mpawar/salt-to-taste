import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:1522/postgres', timeout=2)
        print("Success: postgres:postgres@localhost:1522/postgres")
        await conn.close()
    except Exception as e:
        print(f"Error 1: {e}")
        try:
            conn = await asyncpg.connect('postgresql://system:student@localhost:1522/postgres', timeout=2)
            print("Success: system:student@localhost:1522/postgres")
            await conn.close()
        except Exception as e2:
            print(f"Error 2: {e2}")

asyncio.run(test())
