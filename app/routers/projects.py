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



@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    """Retrieves a single project."""
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.patch("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    """Updates a project."""
    db_project = crud.update_project(db, project_id=project_id, project_update=project_update)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Deletes a project."""
    success = crud.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"detail": "Project successfully deleted"}