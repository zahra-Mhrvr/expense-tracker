from datetime import date as date_type

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models, schemas


def create_expense(db: Session, expense: schemas.ExpenseCreate) -> models.Expense:
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def list_expenses(
    db: Session,
    month: str | None = None,  # "YYYY-MM"
    category: str | None = None,
) -> list[models.Expense]:
    query = db.query(models.Expense)

    if month:
        year, month_num = month.split("-")
        query = query.filter(
            func.strftime("%Y", models.Expense.date) == year,
            func.strftime("%m", models.Expense.date) == month_num,
        )
    if category:
        query = query.filter(models.Expense.category == category)

    return query.order_by(models.Expense.date.desc()).all()


def delete_expense(db: Session, expense_id: int) -> bool:
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        return False
    db.delete(db_expense)
    db.commit()
    return True


def get_summary(db: Session, month: str | None = None) -> schemas.Summary:
    expenses = list_expenses(db, month=month)

    total = sum(e.amount for e in expenses)
    by_category: dict[str, float] = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0.0) + e.amount

    category_totals = [
        schemas.CategoryTotal(category=cat, total=round(total_amt, 2))
        for cat, total_amt in sorted(by_category.items(), key=lambda kv: -kv[1])
    ]

    return schemas.Summary(
        total_spent=round(total, 2),
        expense_count=len(expenses),
        by_category=category_totals,
    )
