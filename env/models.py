from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List

class Patient(BaseModel):
    id: str
    age: int
    sex: Literal['male', 'female', 'other']
    conditions: List[str]
    medications: List[str]
    labs: Dict[str, float]
    consent_signed: bool

class Protocol(BaseModel):
    id: str
    name: str
    inclusion: List[str]
    exclusion: List[str]
    required_labs: Dict[str, Dict[str, float]]
    banned_medications: List[str]

class Observation(BaseModel):
    protocol_id: str
    protocol_name: str
    patient: Patient
    remaining: int

class Action(BaseModel):
    decision: Literal['approve', 'reject', 'request_more_info']
    rationale: Optional[str] = Field(default='')

class Reward(BaseModel):
    value: float
    details: Dict[str, Any]
