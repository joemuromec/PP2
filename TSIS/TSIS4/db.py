# db.py — PostgreSQL persistence layer (psycopg2)

#   CREATE TABLE players (
#       id       SERIAL PRIMARY KEY,
#       username VARCHAR(50) UNIQUE NOT NULL
#   );
#   CREATE TABLE game_sessions (
#       id            SERIAL PRIMARY KEY,
#       player_id     INTEGER REFERENCES players(id),
#       score         INTEGER   NOT NULL,
#       level_reached INTEGER   NOT NULL,
#       played_at     TIMESTAMP DEFAULT NOW()
#   );

import os
from datetime import datetime

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False

# ── Fallback in-memory store (used when DB is unreachable) ───────────────────
_memory_sessions: list[dict] = []

# ─────────────────────────────────────────────────────────────────────────────
def _get_conn():
    """Return a new psycopg2 connection or raise RuntimeError."""
    if not _PSYCOPG2_AVAILABLE:
        raise RuntimeError("psycopg2 not installed")
    dsn = "postgresql://postgres:12345678@localhost:5432/snakegame"
    return psycopg2.connect(dsn)


def init_db():
    """Create tables if they don't exist yet."""
    ddl = """
    CREATE TABLE IF NOT EXISTS players (
        id       SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS game_sessions (
        id            SERIAL PRIMARY KEY,
        player_id     INTEGER REFERENCES players(id),
        score         INTEGER   NOT NULL,
        level_reached INTEGER   NOT NULL,
        played_at     TIMESTAMP DEFAULT NOW()
    );
    """
    try:
        conn = _get_conn()
        with conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
        conn.close()
        return True
    except Exception as e:
        print(f"[db] init_db failed: {e}")
        return False


def _get_or_create_player(cur, username: str) -> int:
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO players (username) VALUES (%s) RETURNING id", (username,)
    )
    return cur.fetchone()[0]


def save_session(username: str, score: int, level_reached: int) -> bool:
    """
    Persist one game session.
    Returns True on success, False on any error (falls back to memory store).
    """
    entry = {
        "username":      username,
        "score":         score,
        "level_reached": level_reached,
        "played_at":     datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    try:
        conn = _get_conn()
        with conn:
            with conn.cursor() as cur:
                pid = _get_or_create_player(cur, username)
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (pid, score, level_reached),
                )
        conn.close()
        return True
    except Exception as e:
        print(f"[db] save_session failed (using memory fallback): {e}")
        _memory_sessions.append(entry)
        return False


def get_top10() -> list[dict]:
    """
    Return top-10 all-time scores as a list of dicts:
      { rank, username, score, level_reached, played_at }
    """
    try:
        conn = _get_conn()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.username,
                       gs.score,
                       gs.level_reached,
                       TO_CHAR(gs.played_at, 'YYYY-MM-DD HH24:MI') AS played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        for i, r in enumerate(rows, 1):
            r["rank"] = i
        return rows
    except Exception as e:
        print(f"[db] get_top10 failed (using memory fallback): {e}")
        return _memory_fallback_top10()


def get_personal_best(username: str) -> int:
    """Return the player's all-time best score, or 0 if none."""
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(gs.score), 0)
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                WHERE p.username = %s
            """, (username,))
            result = cur.fetchone()[0]
        conn.close()
        return int(result)
    except Exception as e:
        print(f"[db] get_personal_best failed: {e}")
        return _memory_personal_best(username)


# ── Memory-store helpers ─────────────────────────────────────────────────────
def _memory_fallback_top10() -> list[dict]:
    combined = sorted(_memory_sessions, key=lambda x: x["score"], reverse=True)[:10]
    return [dict(rank=i+1, **row) for i, row in enumerate(combined)]


def _memory_personal_best(username: str) -> int:
    scores = [s["score"] for s in _memory_sessions if s["username"] == username]
    return max(scores, default=0)