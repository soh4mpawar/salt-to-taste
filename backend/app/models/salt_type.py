from sqlalchemy import String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class SaltType(Base):
    __tablename__ = "salt_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    density_g_per_ml: Mapped[float] = mapped_column(Float, nullable=False)
    sodium_mg_per_gram: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

# Seed Data (Can be used by an alembic data migration or startup script)
SEED_SALT_TYPES = [
    {"name": "Diamond Crystal Kosher", "density_g_per_ml": 0.53, "sodium_mg_per_gram": 393.4, "notes": "Hollow pyramid-shaped crystals, widely used in test kitchens."},
    {"name": "Morton Kosher", "density_g_per_ml": 1.20, "sodium_mg_per_gram": 393.4, "notes": "Dense flakes, about twice as dense as Diamond Crystal."},
    {"name": "Fine Sea Salt", "density_g_per_ml": 1.30, "sodium_mg_per_gram": 393.4, "notes": "Fine granules, similar to table salt."},
    {"name": "Table Salt", "density_g_per_ml": 1.30, "sodium_mg_per_gram": 393.4, "notes": "Dense uniform cubes, often iodized."},
    {"name": "Maldon Flake", "density_g_per_ml": 0.50, "sodium_mg_per_gram": 393.4, "notes": "Large pyramid crystals, usually used for finishing."}
]
