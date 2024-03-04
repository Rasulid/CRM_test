from pydantic import EmailStr

from api.v1 import crud
from api.v1.models import BaseModel, Permission, User, Language, Role, SUPERUSER, STUDENT, MENTOR, CURATOR, Organization
from api.v1.schemas.admin.user.language_schema import ALanguageCreateSchema
from api.v1.schemas.admin.user.organization_schema import ABaseOrganizationSchema
from api.v1.schemas.admin.user.permission_schema import APermissionCreateSchema
from api.v1.schemas.admin.user.role_schema import ARoleCreateSchema
from api.v1.schemas.admin.user.user_schema import AUserCreateWithoutOrganizationSchema, AUserCreateSchema
from core.config import settings
from db.session import SessionLocal

permission_keys = ['create', 'read', 'update', 'delete']

tables_list = list(filter(lambda t: t.rsplit('_')[-1] != 'translation' and not t.startswith("link_"),
                          BaseModel.metadata.tables.keys()))
tables_list += ["resume", "sphere"]

roles_list = [
    {
        "title": SUPERUSER,
    },
    {
        "title": STUDENT,
    },
    {
        "title": MENTOR,
    },
    {
        "title": CURATOR,
    },
]

default_permissions = ['read_user', 'update_user', 'create_user_purchase', 'read_user_purchase',
                       'create_user_pay_history', 'read_course',
                       'read_promocode', 'read_homework_message', 'create_homework_message', 'read_course',
                       'read_course_lesson', 'read_homework_message', 'create_homework_message', 'read_homework',
                       'update_notification', 'read_training', 'update_connected_notification', 'read_quiz_block',
                       'read_answer']


def init_db() -> None:
    with SessionLocal() as db_session:
        # create languages
        languages = [
            ALanguageCreateSchema(title={"en": "Uzbek", "ru": "Узбекский", "uz": "O'zbekcha"}, code="uz"),
            ALanguageCreateSchema(title={"en": "Russian", "ru": "Русский", "uz": "Ruscha"}, code="ru"),
            ALanguageCreateSchema(title={"en": "English", "ru": "Англиский", "uz": "Inglizcha"}, code="en")
        ]
        for language in languages:
            language_obj = crud.language.get(where={Language.code: language.code}, db_session=db_session)
            if not language_obj:
                crud.language.create(language, db_session=db_session)
        print("Languages successfully created!")

        # create organization
        organization = crud.organization.get(where={Organization.identification_number: 308506257},
                                             db_session=db_session)
        if not organization:
            organization = crud.organization.create(
                data=ABaseOrganizationSchema(identification_number=308506257,
                                             translations=[{"language_id": 1, "title": "Topskill"}]),
                db_session=db_session)

        # create roles
        for role_dict in roles_list:
            role = crud.role.get(where={Role.title: role_dict['title'], Role.organization_id: organization.id},
                                 db_session=db_session)
            if not role:
                role = crud.role.create(
                    data=ARoleCreateSchema(title=role_dict['title'], organization_id=organization.id),
                    db_session=db_session)

            # role.add_permissions(default_permissions, db_session=db_session)
        superuser_role = crud.role.get(where={Role.title: SUPERUSER}, db_session=db_session)
        student_role = crud.role.get(where={Role.title: STUDENT}, db_session=db_session)
        print("Roles successfully added!")

        # create permissions
        for table in tables_list:
            for key in permission_keys:
                perm_title = f"{key}_{table}"
                permission = crud.permission.get(where={Permission.title: perm_title}, db_session=db_session)
                if not permission:
                    data = APermissionCreateSchema(title=perm_title, desc="", is_active=True)
                    permission = crud.permission.create(data=data, db_session=db_session)
                    print(perm_title + " successfully added!")

                superuser_role.permissions.append(permission)
                db_session.add(superuser_role)
                db_session.commit()
        print("Permissions successfully added!")

        # createsuperuser
        user = crud.user.get(where={User.email: settings.FIRST_SUPERUSER_EMAIL}, db_session=db_session)
        if not user:
            payload = AUserCreateSchema(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                is_staff=True,
                is_verified=True,
                translations=[],
                organization_id=organization.id
            )
            user = crud.user.create(payload, db_session=db_session)
        user.roles.append(superuser_role)
        db_session.add(user)
        db_session.commit()
        print("Superuser successfully created!")

        # create test student
        user = crud.user.get(where={User.email: "student@student.com"}, db_session=db_session)
        if not user:
            payload = AUserCreateWithoutOrganizationSchema(
                email=EmailStr("student@student.com"),
                hashed_password="student",
                is_superuser=False,
                is_staff=False,
                is_verified=True,
                translations=[],
                organization_id=organization.id
            )
            user = crud.user.create(payload, db_session=db_session)
        user.roles.append(student_role)
        db_session.add(user)
        db_session.commit()
        print("Test student successfully created!")
