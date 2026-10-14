from contextlib import asynccontextmanager
from pathlib import Path

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import text

from backend.auth import router as auth_router
from backend.database import engine, run_migrations
from backend.models import User
from backend.openrouter import send_message_to_openrouter
from backend.security import get_current_user


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_migrations()
    yield


app = FastAPI(
    title="FREE-GPT",
    description="Chat via OpenRouter",
    lifespan=lifespan,
)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.htm"


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Mensagem do usuário")


class SendMessageResponse(BaseModel):
    response: str


HTML_HEADERS = {"Cache-Control": "no-store, no-cache, must-revalidate"}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(INDEX_FILE, media_type="text/html; charset=utf-8", headers=HTML_HEADERS)


@app.get("/index.htm")
def index_htm() -> FileResponse:
    return FileResponse(INDEX_FILE, media_type="text/html; charset=utf-8", headers=HTML_HEADERS)


@app.get("/health")
def health() -> dict:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    dialect = engine.url.get_backend_name()
    return {"status": "ok", "database": dialect}


@app.post("/send_message", response_model=SendMessageResponse)
def send_message(
    body: SendMessageRequest,
    _user: User = Depends(get_current_user),
) -> SendMessageResponse:
    try:
        content = send_message_to_openrouter(body.message.strip())
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Falha na requisição: {exc}") from exc

    return SendMessageResponse(response=content)


app.mount(
    "/lumina-video",
    StaticFiles(directory=FRONTEND_DIR / "lumina-video"),
    name="lumina-video",
)
