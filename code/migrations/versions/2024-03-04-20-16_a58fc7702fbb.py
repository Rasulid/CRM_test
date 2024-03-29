"""add models

Revision ID: a58fc7702fbb
Revises: c46d98addcb8
Create Date: 2024-03-04 20:16:46.817640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a58fc7702fbb'
down_revision: Union[str, None] = 'c46d98addcb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('curator_info_translation', sa.Column('language_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'curator_info_translation', ['curator_info_id', 'language_id'])
    op.create_foreign_key(None, 'curator_info_translation', 'language', ['language_id'], ['id'])
    op.add_column('district', sa.Column('region_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'district', 'region', ['region_id'], ['id'], ondelete='CASCADE')
    op.add_column('district_translation', sa.Column('district_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'district_translation', ['district_id', 'language_id'])
    op.create_foreign_key(None, 'district_translation', 'district', ['district_id'], ['id'], ondelete='CASCADE')
    op.add_column('link_mentor_course', sa.Column('course_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'link_mentor_course', 'course', ['course_id'], ['id'], ondelete='CASCADE')
    op.add_column('link_role_permission', sa.Column('role_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'link_role_permission', 'role', ['role_id'], ['id'], ondelete='CASCADE')
    op.add_column('mentor_info_translation', sa.Column('language_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'mentor_info_translation', ['mentor_info_id', 'language_id'])
    op.create_foreign_key(None, 'mentor_info_translation', 'language', ['language_id'], ['id'])
    op.add_column('organization', sa.Column('legal_address_region_id', sa.Integer(), nullable=True))
    op.add_column('organization', sa.Column('legal_address_district_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'organization', 'district', ['legal_address_district_id'], ['id'])
    op.create_foreign_key(None, 'organization', 'region', ['legal_address_region_id'], ['id'])
    op.add_column('organization_translation', sa.Column('organization_id', sa.UUID(), nullable=False))
    op.add_column('organization_translation', sa.Column('language_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'organization_translation', ['organization_id', 'language_id'])
    op.create_foreign_key(None, 'organization_translation', 'organization', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'organization_translation', 'language', ['language_id'], ['id'])
    op.add_column('region_translation', sa.Column('region_id', sa.Integer(), nullable=False))
    op.add_column('region_translation', sa.Column('language_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'region_translation', ['region_id', 'language_id'])
    op.create_foreign_key(None, 'region_translation', 'region', ['region_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'region_translation', 'language', ['language_id'], ['id'])
    op.add_column('role', sa.Column('organization_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'role', 'organization', ['organization_id'], ['id'])
    op.add_column('student_info', sa.Column('mentor_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'student_info', 'mentor_info', ['mentor_id'], ['id'])
    op.add_column('student_info_translation', sa.Column('language_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'student_info_translation', ['student_info_id', 'language_id'])
    op.create_foreign_key(None, 'student_info_translation', 'language', ['language_id'], ['id'])
    op.add_column('user', sa.Column('region_id', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('district_id', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('organization_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_organization_users', 'user', 'organization', ['organization_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key(None, 'user', 'district', ['district_id'], ['id'])
    op.create_foreign_key(None, 'user', 'region', ['region_id'], ['id'])
    op.add_column('user_translation', sa.Column('language_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'user_translation', ['user_id', 'language_id'])
    op.create_foreign_key(None, 'user_translation', 'language', ['language_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_translation', type_='foreignkey')
    op.drop_constraint(None, 'user_translation', type_='unique')
    op.drop_column('user_translation', 'language_id')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint('fk_organization_users', 'user', type_='foreignkey')
    op.drop_column('user', 'organization_id')
    op.drop_column('user', 'district_id')
    op.drop_column('user', 'region_id')
    op.drop_constraint(None, 'student_info_translation', type_='foreignkey')
    op.drop_constraint(None, 'student_info_translation', type_='unique')
    op.drop_column('student_info_translation', 'language_id')
    op.drop_constraint(None, 'student_info', type_='foreignkey')
    op.drop_column('student_info', 'mentor_id')
    op.drop_constraint(None, 'role', type_='foreignkey')
    op.drop_column('role', 'organization_id')
    op.drop_constraint(None, 'region_translation', type_='foreignkey')
    op.drop_constraint(None, 'region_translation', type_='foreignkey')
    op.drop_constraint(None, 'region_translation', type_='unique')
    op.drop_column('region_translation', 'language_id')
    op.drop_column('region_translation', 'region_id')
    op.drop_constraint(None, 'organization_translation', type_='foreignkey')
    op.drop_constraint(None, 'organization_translation', type_='foreignkey')
    op.drop_constraint(None, 'organization_translation', type_='unique')
    op.drop_column('organization_translation', 'language_id')
    op.drop_column('organization_translation', 'organization_id')
    op.drop_constraint(None, 'organization', type_='foreignkey')
    op.drop_constraint(None, 'organization', type_='foreignkey')
    op.drop_column('organization', 'legal_address_district_id')
    op.drop_column('organization', 'legal_address_region_id')
    op.drop_constraint(None, 'mentor_info_translation', type_='foreignkey')
    op.drop_constraint(None, 'mentor_info_translation', type_='unique')
    op.drop_column('mentor_info_translation', 'language_id')
    op.drop_constraint(None, 'link_role_permission', type_='foreignkey')
    op.drop_column('link_role_permission', 'role_id')
    op.drop_constraint(None, 'link_mentor_course', type_='foreignkey')
    op.drop_column('link_mentor_course', 'course_id')
    op.drop_constraint(None, 'district_translation', type_='foreignkey')
    op.drop_constraint(None, 'district_translation', type_='unique')
    op.drop_column('district_translation', 'district_id')
    op.drop_constraint(None, 'district', type_='foreignkey')
    op.drop_column('district', 'region_id')
    op.drop_constraint(None, 'curator_info_translation', type_='foreignkey')
    op.drop_constraint(None, 'curator_info_translation', type_='unique')
    op.drop_column('curator_info_translation', 'language_id')
    # ### end Alembic commands ###
