import asyncio
import asyncpg
import json
import datetime
from uuid import UUID

def default(o):
    if isinstance(o, (datetime.datetime, datetime.date)):
        return o.isoformat()
    if isinstance(o, UUID):
        return str(o)
    return str(o)

async def main():
    try:
        conn = await asyncpg.connect('postgresql://neondb_owner:npg_FYCUS4VcJH1s@ep-round-thunder-aoslkt9b.c-2.ap-southeast-1.aws.neon.tech/neondb?ssl=require')
        
        print("--- RECIPES ---")
        recipes = await conn.fetch("SELECT * FROM recipes ORDER BY created_at DESC LIMIT 1")
        for r in recipes:
            print(json.dumps(dict(r), default=default, indent=2))
            
        print("--- RECOMMENDATIONS ---")
        recs = await conn.fetch("SELECT * FROM recipe_salt_recommendations ORDER BY created_at DESC LIMIT 1")
        for r in recs:
            print(json.dumps(dict(r), default=default, indent=2))
            
        await conn.close()
    except Exception as e:
        print(f"DB Connection Error: {e}")

asyncio.run(main())
