from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from fastapi import HTTPException


ModelType = TypeVar("ModelType")


class DuplicatedEntryError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=422, detail=message)


class CustomValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class IdOrSlugNotFoundException(HTTPException, Generic[ModelType]):
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)


class ForbiddenError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Forbidden")
