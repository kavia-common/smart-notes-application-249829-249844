"""Pydantic models (schemas) used by the Notes API."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TagOut(BaseModel):
    """Tag representation returned to clients."""

    id: int = Field(..., description="Tag identifier.")
    name: str = Field(..., description="Tag name (unique).")

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    """Common fields for note creation/update."""

    title: str = Field("", max_length=200, description="Note title.")
    content: str = Field("", description="Note body content (markdown/plain text).")
    tags: List[str] = Field(default_factory=list, description="List of tag names applied to the note.")


class NoteCreate(NoteBase):
    """Payload to create a note."""


class NoteUpdate(BaseModel):
    """Payload to update a note (partial)."""

    title: Optional[str] = Field(None, max_length=200, description="New title.")
    content: Optional[str] = Field(None, description="New content.")
    tags: Optional[List[str]] = Field(None, description="Replace tags with this list of tag names.")


class NoteOut(BaseModel):
    """Note representation returned to clients."""

    id: int = Field(..., description="Note identifier.")
    title: str = Field(..., description="Note title.")
    content: str = Field(..., description="Note content.")
    created_at: datetime = Field(..., description="Created timestamp (UTC).")
    updated_at: datetime = Field(..., description="Last updated timestamp (UTC).")
    tags: List[TagOut] = Field(default_factory=list, description="Tags associated to this note.")

    class Config:
        from_attributes = True
