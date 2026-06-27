from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.salt_type import SaltType

SALT_DENSITY_G_PER_ML = {
    "diamond_crystal_kosher": 4.8,   # g per 5ml tsp
    "morton_kosher": 7.7,
    "fine_sea_salt": 5.7,
    "table_salt": 5.9,
    "maldon_flake": 2.8,
}

SALT_SODIUM_PERCENT = {
    "diamond_crystal_kosher": 0.393,
    "morton_kosher": 0.480,
    "fine_sea_salt": 0.387,
    "table_salt": 0.393,
    "maldon_flake": 0.390,
}

SALT_NAME_TO_KEY = {
    "Diamond Crystal Kosher": "diamond_crystal_kosher",
    "Morton Kosher": "morton_kosher",
    "Fine Sea Salt": "fine_sea_salt",
    "Table Salt": "table_salt",
    "Maldon Flake": "maldon_flake",
}

async def get_salt_types_from_db(db: AsyncSession) -> dict[int, dict]:
    try:
        result = await db.execute(select(SaltType))
        salts = result.scalars().all()
        return {
            s.id: {
                "name": s.name,
                "density": s.density_g_per_ml,
                "sodium_percent": s.sodium_mg_per_gram / 1000.0 if s.sodium_mg_per_gram else 0.393
            } for s in salts
        }
    except Exception:
        # Fallback to hardcoded if DB fails
        return {
            i + 1: {
                "name": name,
                "density": SALT_DENSITY_G_PER_ML[key],
                "sodium_percent": SALT_SODIUM_PERCENT[key]
            } for i, (name, key) in enumerate(SALT_NAME_TO_KEY.items())
        }

def convert_salt(from_name: str, to_name: str, amount_grams: float) -> dict:
    if from_name not in SALT_NAME_TO_KEY:
        raise ValueError(f"Unknown salt type: {from_name}")
    if to_name not in SALT_NAME_TO_KEY:
        raise ValueError(f"Unknown salt type: {to_name}")
        
    from_key = SALT_NAME_TO_KEY[from_name]
    to_key = SALT_NAME_TO_KEY[to_name]
    
    # Calculate sodium in the source amount
    sodium_mg = amount_grams * 1000 * SALT_SODIUM_PERCENT[from_key]
    
    # Calculate target grams needed to match that sodium
    target_grams = sodium_mg / (1000 * SALT_SODIUM_PERCENT[to_key])
    
    # Calculate volume equivalents
    # Density is grams per 5ml (1 tsp)
    from_ml = amount_grams / (SALT_DENSITY_G_PER_ML[from_key] / 5)
    to_ml = target_grams / (SALT_DENSITY_G_PER_ML[to_key] / 5)
    
    return {
        "from_salt": from_name,
        "to_salt": to_name,
        "input_grams": round(amount_grams, 2),
        "converted_grams": round(target_grams, 2),
        "input_ml": round(from_ml, 2),
        "converted_ml": round(to_ml, 2),
        "input_tsp": round(from_ml / 5, 2),
        "converted_tsp": round(to_ml / 5, 2),
        "sodium_mg": round(sodium_mg, 1),
        "notes": f"Both amounts contain {round(sodium_mg, 1)}mg sodium"
    }

def get_all_conversion_ratios(from_name: str, amount_grams: float) -> list[dict]:
    results = []
    for to_name in SALT_NAME_TO_KEY.keys():
        if to_name != from_name:
            results.append(convert_salt(from_name, to_name, amount_grams))
    return results
