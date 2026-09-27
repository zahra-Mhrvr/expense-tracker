from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import Base, engine, get_db
from backend.models import CATEGORIES

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/api/categories")
def get_categories():
    return CATEGORIES


@app.post("/api/expenses", response_model=schemas.Expense, status_code=201)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db, expense)


@app.get("/api/expenses", response_model=list[schemas.Expense])
def list_expenses(
    month: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    return crud.list_expenses(db, month=month, category=category)


@app.delete("/api/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_expense(db, expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")


@app.get("/api/summary", response_model=schemas.Summary)
def get_summary(month: str | None = None, db: Session = Depends(get_db)):
    return crud.get_summary(db, month=month)


# serve the frontend as static files, API routes above take priority
# since they're registered first
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")
