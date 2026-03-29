import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from starlette.templating import Jinja2Templates


feedback_router = APIRouter(tags=["Feedback"], prefix="/feedback")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


class ExperienceFeedback(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)
    context: str = Field(default="report", max_length=100)


class FeedbackStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._db_path = Path(__file__).resolve().parent / "data" / "experience_feedback.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS experience_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                    comment TEXT NOT NULL DEFAULT '',
                    context TEXT NOT NULL DEFAULT 'report',
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def insert(self, payload: ExperienceFeedback) -> dict:
        created_at = datetime.now(timezone.utc).isoformat()
        clean_comment = payload.comment.strip()
        clean_context = payload.context.strip() or "report"

        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO experience_feedback (rating, comment, context, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (payload.rating, clean_comment, clean_context, created_at),
            )
            connection.commit()

        return {
            "id": cursor.lastrowid,
            "rating": payload.rating,
            "comment": clean_comment,
            "context": clean_context,
            "created_at": created_at,
        }

    def summary(self) -> dict:
        with self._lock, self._connect() as connection:
            totals = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_responses,
                    COALESCE(ROUND(AVG(rating), 2), 0) AS average_rating
                FROM experience_feedback
                """
            ).fetchone()
            distribution_rows = connection.execute(
                """
                SELECT rating, COUNT(*) AS count
                FROM experience_feedback
                GROUP BY rating
                ORDER BY rating DESC
                """
            ).fetchall()
            recent_rows = connection.execute(
                """
                SELECT rating, comment, context, created_at
                FROM experience_feedback
                ORDER BY id DESC
                LIMIT 5
                """
            ).fetchall()

        distribution = {str(rating): 0 for rating in range(1, 6)}
        for row in distribution_rows:
            distribution[str(row["rating"])] = row["count"]

        return {
            "total_responses": totals["total_responses"],
            "average_rating": totals["average_rating"],
            "distribution": distribution,
            "recent_feedback": [
                {
                    "rating": row["rating"],
                    "comment": row["comment"],
                    "context": row["context"],
                    "created_at": row["created_at"],
                }
                for row in recent_rows
            ],
        }


store = FeedbackStore()


@feedback_router.get("/", response_class=HTMLResponse)
async def feedback_page(request: Request):
    return templates.TemplateResponse(request, "feedback.html", {"request": request})


@feedback_router.post("/experience")
async def create_feedback(payload: ExperienceFeedback):
    try:
        saved_feedback = store.insert(payload)
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Failed to store feedback.") from exc

    return {
        "message": "Feedback recorded.",
        "feedback": saved_feedback,
    }


@feedback_router.get("/experience/summary")
async def get_feedback_summary():
    try:
        return store.summary()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Failed to load feedback summary.") from exc
