"""FastAPI application — HTTP interface for the country agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from country_agent.settings import get_settings

app = FastAPI(title="Country Agent API", version="0.1.0")

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


@app.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest) -> AskResponse:
    from country_agent.main import _run

    answer = await _run(body.question)
    return AskResponse(answer=answer)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
