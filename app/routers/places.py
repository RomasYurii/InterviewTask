from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, services
from ..database import get_db

router = APIRouter(
    prefix="/projects/{project_id}/places",
    tags=["Places"]
)


@router.post("/", response_model=schemas.PlaceResponse)
async def add_place_to_project(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(get_db)):
    """Adds a place to project."""
    is_valid = await services.verify_art_institute_place(place.external_id)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Place with ID {place.external_id} not found in Art Institute API."
        )

    return crud.add_place_to_project(db=db, project_id=project_id, place=place)


@router.patch("/{place_id}", response_model=schemas.PlaceResponse)
def update_place(project_id: int, place_id: int, place_update: schemas.PlaceUpdate, db: Session = Depends(get_db)):
    """Updates a place."""
    updated_place = crud.update_place(db=db, place_id=place_id, place_update=place_update)

    if not updated_place:
        raise HTTPException(status_code=404, detail="Place not found")

    return updated_place


@router.get("/", response_model=List[schemas.PlaceResponse])
def get_project_places(project_id: int, db: Session = Depends(get_db)):
    """Retrieves all projects."""
    project = crud.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.places


@router.get("/{place_id}", response_model=schemas.PlaceResponse)
def get_single_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    """Retrieves a single place."""
    place = crud.get_place(db=db, project_id=project_id, place_id=place_id)

    if not place:
        raise HTTPException(status_code=404, detail="Place not found in this project")

    return place
