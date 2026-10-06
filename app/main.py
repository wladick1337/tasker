from fastapi import FastAPI

from app.database import Base, engine
from app.models import Task

from app.routers import tasks

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(tasks.router, prefix="/tasks")

@app.get("/")
def status():
    return{"status": "Fine!"}


@app.get("/health")
def health():
    return{"status": "ok"}