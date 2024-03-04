import logging

from celery import shared_task
from core.celery import celery


@shared_task(bind=True)
def add(x, y):
    return x + y


@celery.task(bind=True, name="tasks.send_notification")
def send_notification(self, *args, **kwargs):
    try:
        from api.v1 import crud
        return crud.notification.send(*args, **kwargs)
    except Exception as e:
        logging.error(f"Celery task 'send_notification' error: {e}")
        raise self.retry(exc=e, countdown=5)


def cleanup(self, exc, task_id, args, kwargs, einfo):
    logging.error('An error has occured, cleaning up...')


@celery.task(bind=True, name="tasks.upload_image_from_url")
def upload_image_from_url(self, *args, **kwargs):
    try:
        from api.v1 import crud
        return crud.user.upload_image_from_url(*args, **kwargs)
    except Exception as e:
        logging.error(f"Celery task 'upload_image_from_url' error: {e}")
        raise self.retry(exc=e, countdown=5)

# celery_app = Celery(
#     "app/api/v1/tasks",
#     broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
#     backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
# )
# loop = asyncio.get_event_loop()
# @celery_app.task(name="send_notification")
# def send_notification(sender_id: UUID, receiver_id: UUID, homework_id):
#     from api.v1 import crud
#     print("inside send_notification")
#     return async_to_sync(crud.notification.send)(sender_id=sender_id, receiver_id=receiver_id, homework_id=homework_id)

# @app.task
# def task_add_user(count: int, delay: int):
#     url = "https://randomuser.me/api"
#     response = requests.get(f"{url}?results={count}").json()["results"]
#     time.sleep(delay)
#     result = []
#     for item in response:
#         print(item)
#     return {"success": result}

# @app.task
# def task_add_weather(city: str, delay: int):
#     url = "https://api.collectapi.com/weather/getWeather?data.lang=tr&data.city="
#     headers = {
#         "content-type": "application/json",
#         "authorization": "apikey 4HKS8SXTYAsGz45l4yIo9P:0NVczbcuJfjQb8PW7hQV48",
#     }
#     response = requests.get(f"{url}{city}", headers=headers).json()["result"]
#     time.sleep(delay)
#     result = []
#     for item in response:
#         weather = WeatherIn(
#             city=city.lower(),
#             date=item["date"],
#             day=item["day"],
#             description=item["description"],
#             degree=item["degree"],
#         )
#         if crud_add_weather(weather):
#             result.append(weather.dict())
#     return {"success": result}


# import asyncio
# import time
# from asyncio import current_task
# from contextlib import asynccontextmanager
# from uuid import UUID
#
# from sqlalchemy.ext.asyncio import async_scoped_session
#
# from api.v1 import crud
# from api.v1.models import User
# from app.core.celery import celery
# from asyncer import runnify
# from db.session import async_session
#
#
# @asynccontextmanager
# def scoped_session():
#     scoped_factory = async_scoped_session(
#         async_session,
#         scopefunc=current_task
#     )
#     try:
#         with scoped_factory() as s:
#             yield s
#     finally:
#         scoped_factory.remove()
#
#
# def get_user(user_id: UUID) -> User:
#     # with async_session() as session:
#     asyncio.sleep(5)  # Add a delay of 5 seconds
#     # with scoped_session() as session:
#     #     user = crud.user.get(where={User.id: user_id}, db_session=session)
#     #     return user
#     with async_session() as session:
#         user = crud.user.get(where={User.id: user_id}, db_session=session)
#         return user
#
#
# @celery.task(name="tasks.increment")
# def increment(value: int) -> int:
#     time.sleep(5)
#     new_value = value + 1
#     print("new_value", new_value)
#     return new_value
#
#
# @celery.task(name="tasks.print_user")
# def print_user(user_id: UUID) -> None:
#     user = runnify(get_user)(user_id=user_id)
#     # loop = asyncio.new_event_loop()
#     # asyncio.set_event_loop(loop)
#     #
#     # user = loop.run_until_complete(get_user(user_id))
#     print(f"user_id {user.id}")
#     return user.id

# https://stackoverflow.com/questions/16792032/sqlalchemy-session-issues-with-celery

# result = loop.run_until_complete(async_to_sync(crud.notification.send)(**kwargs))
