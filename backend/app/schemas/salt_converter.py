from pydantic import BaseModel, ConfigDict

class SaltConversionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    from_salt_name: str
    to_salt_name: str
    amount_grams: float

class SaltConversionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    from_salt: str
    to_salt: str
    input_grams: float
    converted_grams: float
    input_ml: float
    converted_ml: float
    input_tsp: float
    converted_tsp: float
    sodium_mg: float
    notes: str
