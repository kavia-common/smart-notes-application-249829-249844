from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.notes import router as notes_router
from src.db import init_db_schema

openapi_tags = [
    {
        "name": "System",
        "description": "Health and system endpoints.",
    },
    {
        "name": "Notes",
        "description": "Create, read, update, delete notes; search and filter.",
    },
    {
        "name": "Tags",
        "description": "List tags and tag statistics.",
    },
]

app = FastAPI(
    title="Smart Notes API",
    description="Backend API for a full-stack notes application (notes CRUD, search, tags).",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend origin.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    # Auto-create schema for developer convenience.
    await init_db_schema()


@app.get(
    "/",
    tags=["System"],
    summary="Health check",
    description="Simple health check endpoint.",
    operation_id="health_check",
)
async def health_check() -> dict:
    """Return service health status."""
    return {"message": "Healthy"}


app.include_router(notes_router)
