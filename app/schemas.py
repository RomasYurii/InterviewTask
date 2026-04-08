from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


class PlaceBase(BaseModel):
    external_id: int
    notes: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None

class PlaceResponse(PlaceBase):
    id: int
    project_id: int
    is_visited: bool

    model_config = {"from_attributes": True}



class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    places: List[PlaceCreate] = Field(..., min_length=1, max_length=10)

    @field_validator('places')
    @classmethod
    def check_unique_places(cls, places):
        external_ids = [place.external_id for place in places]
        if len(external_ids) != len(set(external_ids)):
            raise ValueError('Duplicate places are not allowed in the same project')
        return places

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectResponse(ProjectBase):
    id: int
    places: List[PlaceResponse] = []

    model_config = {"from_attributes": True}