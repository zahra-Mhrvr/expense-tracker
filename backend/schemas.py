from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    description: str
    amount: float = Field(gt=0)
    category: str = "Other"
    date: date_type


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryTotal(BaseModel):
    category: str
    total: float


class Summary(BaseModel):
    total_spent: float
    expense_count: int
    by_category: list[CategoryTotal]
