import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_SQLITE_URL = f"sqlite:///{(DATA_DIR / 'lumina.db').as_posix()}"


def _normalize_database_url(raw: str) -> str:
    """Accept Neon/Render URLs (postgres:// or postgresql://) for SQLAlchemy + psycopg."""
    if raw.startswith("postgres://"):
        raw = "postgresql://" + raw.removeprefix("postgres://")
    if raw.startswith("postgresql://") and not raw.startswith("postgresql+"):
        raw = "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    return raw


def _resolve_database_url(raw: str) -> str:
    """Keep SQLite paths anchored to the project; normalize Postgres URLs."""
    raw = _normalize_database_url(raw)
    if raw.startswith("sqlite:///./"):
        relative = raw.removeprefix("sqlite:///")
        return f"sqlite:///{(PROJECT_ROOT / relative).as_posix()}"
    return raw


DATABASE_URL = _resolve_database_url(
    (os.getenv("DATABASE_URL") or DEFAULT_SQLITE_URL).strip()
)
SECRET_KEY = (os.getenv("SECRET_KEY") or "").strip()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
