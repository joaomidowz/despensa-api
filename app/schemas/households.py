from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class HouseholdCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)


class HouseholdResponse(BaseModel):
    household_id: UUID
    name: str
    owner_id: UUID


class GenerateInviteRequest(BaseModel):
    household_id: UUID


class GenerateInviteResponse(BaseModel):
    invite_token: str
    invite_url: HttpUrl
    expires_at: datetime


class JoinHouseholdRequest(BaseModel):
    invite_token: str


class JoinHouseholdResponse(BaseModel):
    message: str
    household_id: UUID
    household_name: str

