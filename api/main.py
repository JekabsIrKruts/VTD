"""HTTP endpoints for leaderboard scores, browser pages, and admin actions."""

import hmac
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse

from api.db import (
    delete_all_scores,
    delete_score,
    get_all_scores,
    get_top_scores,
    initialize_database,
    save_score,
)

initialize_database()
app = FastAPI()
LEADERBOARD_PAGE = Path(__file__).with_name("leaderboard.html")
ADMIN_PAGE = Path(__file__).with_name("admin.html")
ADMIN_COOKIE = "vtd_admin_session"
ADMIN_SESSIONS = set()


def get_admin_password():
    """Load the admin login secret from the environment or api/.env."""
    password = os.environ.get("VTD_ADMIN_PASSWORD")
    if password:
        return password

    env_file = Path(__file__).with_name(".env")
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "VTD_ADMIN_PASSWORD":
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            return value or None
    return None


# PUBLIC PAGES AND SCORE SUBMISSION
@app.get("/", include_in_schema=False)
def show_leaderboard():
    """Serve the public leaderboard page at the site root."""
    return FileResponse(LEADERBOARD_PAGE)


@app.get("/admin", include_in_schema=False)
def show_admin_page():
    """Serve the password-protected admin interface."""
    return FileResponse(ADMIN_PAGE)


class ScoreSubmission(BaseModel):
    """Validate the username and score sent by the game client."""

    username: str = Field(min_length=1, max_length=20)
    score: int = Field(ge=0)


@app.post("/scores", status_code=201)
def submit_score(submission: ScoreSubmission):
    """Validate and save one player's completed game score."""
    username = submission.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username cannot be blank.")

    save_score(username, submission.score)
    return {"message": "Score saved", "username": username, "score": submission.score}


@app.get("/scores/top")
def read_top_scores():
    """Return the ten highest saved scores for the public leaderboard."""
    return get_top_scores()


class AdminLogin(BaseModel):
    """Validate a password submitted by the admin login form."""

    password: str = Field(min_length=1)


def require_admin(request: Request):
    """Reject an admin request unless its session cookie is valid."""
    session = request.cookies.get(ADMIN_COOKIE)
    if not session or session not in ADMIN_SESSIONS:
        raise HTTPException(status_code=401, detail="Admin login required.")


# ADMIN LOGIN AND SCORE MANAGEMENT
@app.post("/admin/login")
def admin_login(login: AdminLogin, request: Request, response: Response):
    """Verify the admin password and create a short-lived session cookie."""
    expected_password = get_admin_password()
    if not expected_password:
        raise HTTPException(
            status_code=503,
            detail="Admin password is not set in the server environment.",
        )
    if not hmac.compare_digest(login.password, expected_password):
        raise HTTPException(status_code=401, detail="Incorrect password.")

    session = secrets.token_urlsafe(32)
    ADMIN_SESSIONS.add(session)
    response.set_cookie(
        ADMIN_COOKIE,
        session,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        max_age=3600,
        path="/",
    )
    return {"message": "Admin login successful."}


@app.post("/admin/logout")
def admin_logout(request: Request, response: Response):
    """Remove the current admin session and expire its cookie."""
    session = request.cookies.get(ADMIN_COOKIE)
    if session:
        ADMIN_SESSIONS.discard(session)
    response.delete_cookie(ADMIN_COOKIE, path="/")
    return {"message": "Logged out."}


@app.get("/admin/scores")
def read_all_scores(request: Request):
    """Return all saved scores to an authenticated admin."""
    require_admin(request)
    return get_all_scores()


@app.delete("/admin/scores/{score_id}")
def remove_score(score_id: int, request: Request):
    """Delete one saved score by its database ID."""
    require_admin(request)
    if not delete_score(score_id):
        raise HTTPException(status_code=404, detail="Score not found.")
    return {"message": "Score removed."}


@app.delete("/admin/scores")
def remove_all_scores(request: Request):
    """Delete every saved score and return the number removed."""
    require_admin(request)
    return {"deleted": delete_all_scores()}
