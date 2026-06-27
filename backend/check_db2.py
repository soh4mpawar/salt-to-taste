import asyncio
import asyncpg

async def main():
    try:
        conn = await asyncpg.connect('postgresql://neondb_owner:npg_FYCUS4VcJH1s@ep-round-thunder-aoslkt9b.c-2.ap-southeast-1.aws.neon.tech/neondb?ssl=require')
        
        print("--- TABLES ---")
        rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        for r in rows:
            print(r['table_name'])
            
        print("--- SEED DATA ---")
        try:
            seeds = await conn.fetch("SELECT name, sodium_mg_per_gram FROM salt_types")
            for s in seeds:
                print(f"{s['name']}: {s['sodium_mg_per_gram']}")
        except Exception as e:
            print(f"Error querying seed data: {e}")
            
        await conn.close()
    except Exception as e:
        print(f"DB Connection Error: {e}")

asyncio.run(main())
