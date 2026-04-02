import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import List, Dict, Any

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


class FeedbackObjectStore:
    """
    Object storage-based feedback store.
    Stores each feedback entry as a separate JSON object file.
    Can be easily adapted to use S3, GCS, or other cloud object storage.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._storage_path = Path(__file__).resolve().parent / "data" / "feedback"
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._index_file = self._storage_path / "_index.json"
        self._init_index()

    def _init_index(self) -> None:
        """Initialize the index file if it doesn't exist."""
        if not self._index_file.exists():
            self._write_index([])

    def _read_index(self) -> List[str]:
        """Read the index of feedback object IDs."""
        try:
            with open(self._index_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_index(self, index: List[str]) -> None:
        """Write the index of feedback object IDs."""
        with open(self._index_file, "w") as f:
            json.dump(index, f)

    def _get_object_path(self, object_id: str) -> Path:
        """Get the file path for a feedback object."""
        return self._storage_path / f"{object_id}.json"

    def _read_object(self, object_id: str) -> Dict[str, Any] | None:
        """Read a single feedback object from storage."""
        object_path = self._get_object_path(object_id)
        try:
            with open(object_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def _write_object(self, object_id: str, data: Dict[str, Any]) -> None:
        """Write a single feedback object to storage."""
        object_path = self._get_object_path(object_id)
        with open(object_path, "w") as f:
            json.dump(data, f, indent=2)

    def insert(self, payload: ExperienceFeedback) -> Dict[str, Any]:
        """Store a new feedback entry as a JSON object."""
        object_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        clean_comment = payload.comment.strip()
        clean_context = payload.context.strip() or "report"

        feedback_data = {
            "id": object_id,
            "rating": payload.rating,
            "comment": clean_comment,
            "context": clean_context,
            "created_at": created_at,
        }

        with self._lock:
            # Write the feedback object
            self._write_object(object_id, feedback_data)

            # Update the index (prepend for newest-first ordering)
            index = self._read_index()
            index.insert(0, object_id)
            self._write_index(index)

        return feedback_data

    def _list_all_feedback(self) -> List[Dict[str, Any]]:
        """List all feedback entries in order (newest first)."""
        index = self._read_index()
        feedback_list = []
        for object_id in index:
            obj = self._read_object(object_id)
            if obj:
                feedback_list.append(obj)
        return feedback_list

    def summary(self) -> Dict[str, Any]:
        """Generate a summary of all feedback."""
        with self._lock:
            all_feedback = self._list_all_feedback()

        total_responses = len(all_feedback)

        if total_responses == 0:
            return {
                "total_responses": 0,
                "average_rating": 0,
                "distribution": {str(r): 0 for r in range(1, 6)},
                "recent_feedback": [],
            }

        # Calculate average rating
        total_rating = sum(f["rating"] for f in all_feedback)
        average_rating = round(total_rating / total_responses, 2)

        # Calculate distribution
        distribution = {str(r): 0 for r in range(1, 6)}
        for f in all_feedback:
            distribution[str(f["rating"])] += 1

        # Get recent feedback (first 5, already sorted newest-first)
        recent_feedback = [
            {
                "rating": f["rating"],
                "comment": f["comment"],
                "context": f["context"],
                "created_at": f["created_at"],
            }
            for f in all_feedback[:5]
        ]

        return {
            "total_responses": total_responses,
            "average_rating": average_rating,
            "distribution": distribution,
            "recent_feedback": recent_feedback,
        }


store = FeedbackObjectStore()


@feedback_router.get("/", response_class=HTMLResponse)
async def feedback_page(request: Request):
    return templates.TemplateResponse(request, "feedback.html", {"request": request})


@feedback_router.post("/experience")
async def create_feedback(payload: ExperienceFeedback):
    try:
        saved_feedback = store.insert(payload)
    except (IOError, OSError) as exc:
        raise HTTPException(status_code=500, detail="Failed to store feedback.") from exc

    return {
        "message": "Feedback recorded.",
        "feedback": saved_feedback,
    }


@feedback_router.get("/experience/summary")
async def get_feedback_summary():
    try:
        return store.summary()
    except (IOError, OSError) as exc:
        raise HTTPException(status_code=500, detail="Failed to load feedback summary.") from exc
