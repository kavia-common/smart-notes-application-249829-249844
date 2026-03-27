"""Notes and Tags API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.schemas import NoteCreate, NoteOut, NoteUpdate, TagOut
from src.services.notes_service import (
    create_note,
    delete_note,
    get_note,
    list_notes,
    list_tags,
    tag_counts,
    update_note,
)

router = APIRouter(prefix="", tags=["Notes"])


@router.get(
    "/notes",
    response_model=list[NoteOut],
    summary="List notes",
    description="List notes ordered by last updated time. Supports full-text-ish search on title/content and filtering by tag.",
    operation_id="list_notes",
)
async def api_list_notes(
    q: str | None = Query(None, description="Search query matched against title/content (ILIKE)."),
    tag: str | None = Query(None, description="Filter by tag name."),
    limit: int = Query(200, ge=1, le=500, description="Max number of notes to return."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
    session: AsyncSession = Depends(get_db_session),
) -> list[NoteOut]:
    """Return notes for the current workspace/user (no auth in this template)."""
    return await list_notes(session=session, q=q, tag=tag, limit=limit, offset=offset)


@router.post(
    "/notes",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note with optional tags.",
    operation_id="create_note",
)
async def api_create_note(payload: NoteCreate, session: AsyncSession = Depends(get_db_session)) -> NoteOut:
    """Create and return a note."""
    return await create_note(session=session, title=payload.title, content=payload.content, tag_names=payload.tags)


@router.get(
    "/notes/{note_id}",
    response_model=NoteOut,
    summary="Get note",
    description="Get a single note by id.",
    operation_id="get_note",
)
async def api_get_note(note_id: int, session: AsyncSession = Depends(get_db_session)) -> NoteOut:
    """Return a note by id."""
    note = await get_note(session=session, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put(
    "/notes/{note_id}",
    response_model=NoteOut,
    summary="Update note",
    description="Update note fields (title/content) and optionally replace tags list.",
    operation_id="update_note",
)
async def api_update_note(
    note_id: int,
    payload: NoteUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> NoteOut:
    """Update a note."""
    note = await get_note(session=session, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return await update_note(
        session=session,
        note=note,
        title=payload.title,
        content=payload.content,
        tag_names=payload.tags,
    )


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note by id.",
    operation_id="delete_note",
)
async def api_delete_note(note_id: int, session: AsyncSession = Depends(get_db_session)) -> None:
    """Delete a note."""
    await delete_note(session=session, note_id=note_id)
    return None


@router.get(
    "/tags",
    response_model=list[TagOut],
    summary="List tags",
    description="List all tags used across notes.",
    operation_id="list_tags",
    tags=["Tags"],
)
async def api_list_tags(session: AsyncSession = Depends(get_db_session)) -> list[TagOut]:
    """Return tags."""
    return await list_tags(session=session)


@router.get(
    "/tags/counts",
    summary="Tag counts",
    description="Return a mapping of tag name to number of notes with that tag.",
    operation_id="tag_counts",
    tags=["Tags"],
)
async def api_tag_counts(session: AsyncSession = Depends(get_db_session)) -> dict[str, int]:
    """Return tag counts."""
    return await tag_counts(session=session)
