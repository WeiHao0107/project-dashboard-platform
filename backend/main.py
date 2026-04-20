from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import projects, pages, widget_data

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(pages.router)
app.include_router(widget_data.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
