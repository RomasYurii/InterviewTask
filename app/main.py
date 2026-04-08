from fastapi import FastAPI
from . import models
from .database import engine

from .routers import projects, places

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Planner API",
    description="API for managing travel projects and places.",
    version="1.0.0"
)

app.include_router(projects.router)
app.include_router(places.router)