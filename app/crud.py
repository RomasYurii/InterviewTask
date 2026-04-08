from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from . import models, schemas


def get_project(db: Session, project_id: int):
    """ Get one project by ID"""
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    """ Get all projects"""
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    """Create a new project"""
    db_project = models.Project(
        name=project.name,
        description=project.description,
        start_date=project.start_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # 2. Додаємо всі місця до цього проекту
    try:
        for place_in in project.places:
            db_place = models.Place(
                project_id=db_project.id,
                external_id=place_in.external_id,
                notes=place_in.notes
            )
            db.add(db_place)
        db.commit()
        db.refresh(db_project)

    except IntegrityError:
        db.rollback()
        db.delete(db_project)
        db.commit()
        raise HTTPException(status_code=400, detail="Database integrity error while adding places.")

    return db_project

def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate):
    """Update a project"""
    db_project = get_project(db, project_id)
    if not db_project:
        return None

    update_data = project_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    """Delete a project"""
    db_project = get_project(db, project_id)
    if not db_project:
        return None

    if any(place.is_visited for place in db_project.places):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete project. It contains places already marked as visited."
        )

    db.delete(db_project)
    db.commit()
    return True





def add_place_to_project(db: Session, project_id: int, place: schemas.PlaceCreate):
    """Add a place to project"""
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(db_project.places) >= 10:
        raise HTTPException(status_code=400, detail="A project can have a maximum of 10 places.")

    existing_place = db.query(models.Place).filter(
        models.Place.project_id == project_id,
        models.Place.external_id == place.external_id
    ).first()

    if existing_place:
        raise HTTPException(status_code=400, detail="This place is already in the project.")

    new_place = models.Place(
        project_id=project_id,
        external_id=place.external_id,
        notes=place.notes
    )
    db.add(new_place)
    db.commit()
    db.refresh(new_place)
    return new_place


def update_place(db: Session, place_id: int, place_update: schemas.PlaceUpdate):
    """Update a place"""
    db_place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not db_place:
        return None

    if place_update.notes is not None:
        db_place.notes = place_update.notes

    if place_update.is_visited is not None:
        db_place.is_visited = place_update.is_visited

    db.commit()
    db.refresh(db_place)
    return db_place