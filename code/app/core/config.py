# import getpass
# import pathlib
# import socket
#
# from pydantic import PostgresDsn, EmailStr
# from pydantic.v1 import BaseSettings, AnyHttpUrl
# from pydantic_settings import SettingsConfigDict
#
# if getpass.getuser() == "rasulabduvaitov" or socket.gethostname() == "pop-os":
#     env_filename = ".env"
# else:
#     env_filename = ".env.dev"
#
# ENV_FILE_PATH = pathlib.Path(__file__).resolve().parents[1] / env_filename
#
# BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
# TEMPLATES_DIR = pathlib.Path(BASE_DIR, 'templates')
# STATIC_DIR = pathlib.Path(BASE_DIR, 'static')
#
#
# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(env_file=ENV_FILE_PATH)
#     API_VERSION: str = "v1"
#     API_PREFIX: str = f"/api/{API_VERSION}"
#     API_V2_VERSION: str = "v2"
#     API_V2_PREFIX: str = f"/api/{API_V2_VERSION}"
#     SVC_PORT: int
#     TIMEZONE: str = 'Asia/Tashkent'
#     FIRST_SUPERUSER_EMAIL: EmailStr
#     FIRST_SUPERUSER_PASSWORD: str
#     SECRET_KEY: str
#     ENCRYPT_KEY: str
#     # Database
#     DATABASE_PORT: int
#     DATABASE_PASSWORD: str
#     DATABASE_USER: str
#     DATABASE_NAME: str
#     DATABASE_HOST: str
#     # JWT
#     JWT_PUBLIC_KEY: str
#     JWT_PRIVATE_KEY: str
#     REFRESH_TOKEN_EXPIRES_IN: int = 60 * 24 * 10  # 10 days
#     ACCESS_TOKEN_EXPIRES_IN: int = 60  # 60 minutes
#     JWT_ALGORITHM: str
#     # Redis
#     REDIS_HOST: str
#     REDIS_PORT: str
#
#     class Config:
#         env_file = ENV_FILE_PATH
#
#
# settings = Settings()


import os

from dotenv import load_dotenv


class Settings:

    @property
    def database(self) -> str:
        return self.__database

    @property
    def database_host(self) -> str:
        return self.__database_host

    @property
    def database_port(self) -> int:
        return int(self.__database_port)

    @property
    def database_name(self) -> str:
        return self.__database_name

    @property
    def database_user_name(self) -> str:
        return self.__database_user_name

    @property
    def database_pass(self) -> str:
        return self.__database_pass

    @property
    def srv_port(self) -> int:
        return int(self.__srv_port)

    @property
    def project_name(self) -> str:
        return self.__project_name

    @property
    def jwt_algorithm(self) -> str:
        return self.__jwt_algorithm

    @property
    def jwt_private_key(self) -> str:
        return self.__jwt_private_key

    def __init__(self) -> None:
        load_dotenv()
        self.__srv_port = os.environ.get('SVC_PORT')
        self.__project_name = os.environ.get('PROJECT_NAME')
        self.__jwt_algorithm = os.environ.get('JWT_ALGORITHM')
        self.__jwt_private_key = os.environ.get('JWT_PRIVATE_KEY')
        self.__database = os.environ.get('DATABASE')
        self.__database_host = os.environ.get('DATABASE_HOST')
        self.__database_port = os.environ.get('DATABASE_PORT')
        self.__database_name = os.environ.get('DATABASE_NAME')
        self.__database_user_name = os.environ.get('DATABASE_USER')
        self.__database_pass = os.environ.get('DATABASE_PASSWORD')


settings = Settings()
