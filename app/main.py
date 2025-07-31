from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .routes import router  # Your existing API routes

app = FastAPI(
    title="Jeopardy Game API",
    description="An API to play a trivia game with the Jeopardy dataset.",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/api", tags=["Jeopardy"])

@app.get("/", response_class=HTMLResponse, tags=["Root"])
def serve_frontend():
    with open("static/index.html") as f:
        return f.read()
