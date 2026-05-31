from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    product_id: int = Field(example=2)
    online_order: bool = Field(example=False)
    order_status: str = Field(example="Approved")
    brand: str = Field(example="Solex")
    product_line: str = Field(example="Standard")
    product_class: str = Field(example="medium")
    product_size: str = Field(example="medium")
    list_price: float = Field(example=71.49)
    transaction_date: str = Field(example="25.02.2017")


class PredictionResponse(BaseModel):
    predicted_standard_cost: float
    model_version: str
