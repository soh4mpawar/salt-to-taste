from pydantic import BaseModel, ConfigDict

class SaltConversionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    from_salt_type_id: int
    to_salt_type_id: int
    amount_grams: float

class SaltConversionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    converted_amount_grams: float
    converted_amount_ml: float
    notes: str | None = None
