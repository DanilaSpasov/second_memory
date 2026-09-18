from fastapi import FastAPI

from app.notes.routes import router as notes_router


app = FastAPI()
app.include_router(notes_router)


@app.get("/health")
def health():
    return {"status": "ok"}
