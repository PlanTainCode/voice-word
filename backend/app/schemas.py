from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# Record schemas
class RecordCreate(BaseModel):
    title: str


class RecordUpdate(BaseModel):
    title: Optional[str] = None
    processed_text: Optional[str] = None


class RecordResponse(BaseModel):
    id: int
    title: str
    original_text: Optional[str] = None
    processed_text: Optional[str] = None
    audio_file_path: Optional[str] = None
    word_file_path: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecordListResponse(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

