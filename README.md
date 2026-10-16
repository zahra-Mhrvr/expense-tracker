# Ledger — a full-stack expense tracker

A small expense tracker with a real FastAPI backend and a plain HTML/CSS/JS
frontend — no React, no build step, no npm install. Wanted a project that
proved I can build both ends of the stack and wire them together, without
the frontend tooling becoming the whole story.

Add an expense, see it show up in the list and in the category breakdown
immediately. Filter by month. Delete anything you added by mistake.

## Why plain JS instead of React

Mostly so anyone (including future me) can clone this and open it with
zero setup beyond `pip install`. There's no reason this couldn't be a React
frontend instead — the API is a normal JSON REST API and doesn't care what
calls it — but for a project this size, a build step would be adding
complexity without adding much. `frontend/app.js` is under 200 lines of
plain fetch calls and DOM updates.

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** HTML/CSS/vanilla JS, served directly by FastAPI's
  `StaticFiles` (no separate frontend server, no CORS to think about)
- **Tests:** pytest + FastAPI's `TestClient`, against an isolated test
  database

## Setup

```bash
git clone https://github.com/zahra-Mhrvr/expense-tracker.git
cd expense-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running it

```bash
uvicorn backend.main:app --reload
```

Then open `http://localhost:8000` — that's it, frontend and API both come
from the same server. The interactive API docs are at
`http://localhost:8000/docs` if you want to poke at the endpoints directly.

## What it does

- Add an expense: description, amount, category, date
- See the running total for the selected month front and center
- A category breakdown showing where the money's actually going, as
  horizontal bars sized by relative spend
- A ledger-style list of every entry for the month, newest first, with a
  one-click delete
- Switch months with a native month picker — everything refetches for
  that month

## API

| Method | Path                  | Description                          |
|--------|-----------------------|---------------------------------------|
| GET    | /api/categories       | Fixed list of expense categories      |
| POST   | /api/expenses         | Create an expense                     |
| GET    | /api/expenses         | List expenses (`?month=`, `?category=`) |
| DELETE | /api/expenses/{id}    | Delete an expense                     |
| GET    | /api/summary          | Total, count, and per-category totals (`?month=`) |

## Tests

```bash
pytest tests/ -v
```

10 tests covering creation, validation (no zero/negative amounts), month
and category filtering, deletion (including deleting something that
doesn't exist), and summary math.

## Design notes

Went with a plain "ledger" look — paper background, a serif display face
for the numbers, hairline rules between entries instead of cards — since
it's genuinely just a record of transactions, and a stack of rounded
shadow-cards didn't feel like it matched that. The category breakdown is
hand-rolled divs instead of a charting library, partly for the look and
partly because it meant one less script tag and one less thing to keep in
sync with a CDN.

## Things I'd add next

- Auth — right now this is single-user, no login, fine for personal use
  on my own machine, not fine for anything shared
- Editing an existing expense (right now you can only add or delete, not
  edit in place)
- A year-over-year or multi-month view — right now everything is scoped to
  a single selected month

## License

MIT
