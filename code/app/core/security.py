from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2y")


def hash_password(password: str):
    return pwd_context.hash(password, rounds=10)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)
