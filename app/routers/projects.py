from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, services
from ..database import get_db

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/", response_model=schemas.ProjectResponse)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):

    """Creates a project and adds a list of locations to it.
    Validates each location via the Art Institute API before saving."""


    for place in project.places:
        is_valid = await services.verify_art_institute_place(place.external_id)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Place with ID {place.external_id} not found in Art Institute API."
            )

    return crud.create_project(db=db, project=project)


@router.get("/", response_model=List[schemas.ProjectResponse])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves all projects."""
    return crud.get_projects(db, skip=skip, limit=limit)