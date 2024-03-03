import enum
import re
from typing import Callable

from api.v1.exceptions import CustomValidationError
from core.babel_config import _


class PhoneStr(str):

    @classmethod
    def __get_validators__(cls) -> Callable:
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        pattern = r"^998\d{9}$"
        result = re.match(pattern, v)
        if not result:
            raise CustomValidationError(_("Phone number must begin with 998 and contain only 12 numbers"))
        return v


class PasswordStr(str):

    @classmethod
    def __get_validators__(cls) -> Callable:
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        regexp = (
            r"(?=.{5,})"
            # r"(?=.*[a-z]{5,})"
            # r"(?=.*?[A-Z])"
            # r"(?=.*?[0-9])"
        )
        if not re.match(regexp, v):
            raise CustomValidationError(_("Password must contain at least five characters"))
            # raise ValueError(_("Password must contain at least one lower/upper case letter, one digit."))
        return v


class GenderStatusEnum(str, enum.Enum):
    MALE = 'male'
    FEMALE = 'female'


class CourseStatusEnum(str, enum.Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    PREMIERE = 'premiere'


class DifficultyLevelEnum(str, enum.Enum):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    EXPERT = 'expert'


class PaymentProvidersEnum(str, enum.Enum):
    CLICK = 'click'
    PAYCOM = 'paycom'
    UZUM = 'uzum'
    UPAY = 'upay'
    RAHMAT = "rahmat"


class PaymentTypeEnum(str, enum.Enum):
    CASH = "cash"
    PLASTIC = "plastic"


class TokenType(str, enum.Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"


class HomeworkStatusEnum(str, enum.Enum):
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    WAITING = 'waiting'


class QuestionTypeEnum(str, enum.Enum):
    SINGLE = 'single'
    MULTIPLE = 'multiple'
    OWN_ANSWER = 'own_answer'


class QuizBlockTypeEnum(str, enum.Enum):
    LAST_PUBLIC = 'last_public'
    EVERY_PUBLIC = 'every_public'
    LAST_PRIVATE = 'last_private'
    EVERY_PRIVATE = 'every_private'
