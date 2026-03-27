"""
Service layer for Notes.

Keeps DB access logic out of route handlers, making it easier to test and evolve.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Note, Tag, note_tags


async def _get_or_create_tags(session: AsyncSession, tag_names: List[str]) -> List[Tag]:
    cleaned = []
    for name in tag_names:
        n = name.strip()
        if n and n not in cleaned:
            cleaned.append(n)

    if not cleaned:
        return []

    existing = (
        await session.execute(select(Tag).where(Tag.name.in_(cleaned)))
    ).scalars().all()
    existing_by_name = {t.name: t for t in existing}

    tags: List[Tag] = []
    for name in cleaned:
        tag = existing_by_name.get(name)
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            tags.append(tag)
        else:
            tags.append(tag)
    return tags


# PUBLIC_INTERFACE
async def list_notes(
    session: AsyncSession,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> List[Note]:
    """List notes with optional text search and tag filtering."""
    stmt = select(Note).options(selectinload(Note.tags)).order_by(Note.updated_at.desc())
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.content.ilike(like)))
    if tag:
        stmt = stmt.join(Note.tags).where(Tag.name == tag.strip())
    stmt = stmt.limit(min(limit, 500)).offset(max(offset, 0))
    return (await session.execute(stmt)).scalars().unique().all()


# PUBLIC_INTERFACE
async def get_note(session: AsyncSession, note_id: int) -> Optional[Note]:
    """Fetch a single note by id."""
    stmt = select(Note).options(selectinload(Note.tags)).where(Note.id == note_id)
    return (await session.execute(stmt)).scalars().first()


# PUBLIC_INTERFACE
async def create_note(session: AsyncSession, title: str, content: str, tag_names: List[str]) -> Note:
    """Create a note."""
    note = Note(title=title or "", content=content or "")
    note.tags = await _get_or_create_tags(session, tag_names)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


# PUBLIC_INTERFACE
async def update_note(
    session: AsyncSession,
    note: Note,
    title: Optional[str],
    content: Optional[str],
    tag_names: Optional[List[str]],
) -> Note:
    """Update an existing note."""
    if title is not None:
        note.title = title
    if content is not None:
        note.content = content
    if tag_names is not None:
        note.tags = await _get_or_create_tags(session, tag_names)

    await session.commit()
    await session.refresh(note)
    return note


# PUBLIC_INTERFACE
async def delete_note(session: AsyncSession, note_id: int) -> None:
    """Delete a note by id."""
    await session.execute(delete(Note).where(Note.id == note_id))
    await session.commit()


# PUBLIC_INTERFACE
async def list_tags(session: AsyncSession) -> List[Tag]:
    """List tags with note counts (note count computed separately in route)."""
    stmt = select(Tag).order_by(Tag.name.asc())
    return (await session.execute(stmt)).scalars().all()


# PUBLIC_INTERFACE
async def tag_counts(session: AsyncSession) -> dict[str, int]:
    """Return a mapping of tag name -> number of notes having that tag."""
    stmt = (
        select(Tag.name, func.count(note_tags.c.note_id))
        .select_from(Tag)
        .join(note_tags, Tag.id == note_tags.c.tag_id, isouter=True)
        .group_by(Tag.name)
    )
    rows = (await session.execute(stmt)).all()
    return {name: count for name, count in rows}
