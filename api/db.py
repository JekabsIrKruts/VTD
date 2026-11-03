"""SQLite operations for creating and managing leaderboard scores."""

import sqlite3
from contextlib import closing
from pathlib import Path


DB_PATH = Path(__file__).with_name("scores.db")


def initialize_database():
    """Create the scores table if it does not already exist."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    score INTEGER NOT NULL CHECK (score >= 0)
                )
            """)


def save_score(username, score):
    """Insert one validated username and score into the database."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO scores (username, score) VALUES (?, ?)",
                (username, score),
            )


def get_top_scores():
    """Return the ten highest scores for the public leaderboard."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        rows = connection.execute(
            "SELECT username, score FROM scores ORDER BY score DESC LIMIT ?",
            (10,),
        ).fetchall()

    return [
        {"username": row[0], "score": row[1]}
        for row in rows
    ]


def get_all_scores():
    """Return all saved results, ordered by score, for admin management."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        rows = connection.execute(
            "SELECT id, username, score FROM scores ORDER BY score DESC, id ASC"
        ).fetchall()

    return [
        {"id": row[0], "username": row[1], "score": row[2]}
        for row in rows
    ]


def delete_score(score_id):
    """Delete a score by ID and report whether a row was removed."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            cursor = connection.execute("DELETE FROM scores WHERE id = ?", (score_id,))
            return cursor.rowcount > 0


def delete_all_scores():
    """Delete all leaderboard rows and return the number removed."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            cursor = connection.execute("DELETE FROM scores")
            return cursor.rowcount
