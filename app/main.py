from typing import Annotated
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, StringConstraints

NoteText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=4000,
    )
]

class NoteCreate(BaseModel):
    text: NoteText

class Note(BaseModel):
    id: int
    text: NoteText



app = FastAPI()

notes: list[Note] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/notes/{note_id}", response_model=Note)
def read_note(note_id: int):
    for note in notes:
        if note.id == note_id:
            return note

    raise HTTPException(status_code=404, detail="Note not found")

@app.get("/notes", response_model=list[Note])
def read_notes(limit: int = 10):
    return notes[:limit]

@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteCreate):
    saved_note = Note(
        id=len(notes) + 1,
        text=note.text,
    )
    notes.append(saved_note)
    return saved_note