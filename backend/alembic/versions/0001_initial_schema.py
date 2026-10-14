"""initial_schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-10-14 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Bảng companies
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('website', sa.Text(), nullable=True),
        sa.Column('province', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)
    op.create_index(op.f('ix_companies_province'), 'companies', ['province'], unique=False)

    # 2. Bảng provinces
    op.create_table(
        'provinces',
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('code')
    )
    op.create_index(op.f('ix_provinces_name'), 'provinces', ['name'], unique=False)
    op.create_index(op.f('ix_provinces_name_en'), 'provinces', ['name_en'], unique=False)
    op.create_index(op.f('ix_provinces_region'), 'provinces', ['region'], unique=False)

    # 3. Bảng jobs
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('company_name', sa.String(length=300), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('salary_min', sa.BigInteger(), nullable=True),
        sa.Column('salary_max', sa.BigInteger(), nullable=True),
        sa.Column('salary_text', sa.String(length=200), nullable=True),
        sa.Column('location_province', sa.String(length=100), nullable=True),
        sa.Column('location_district', sa.String(length=100), nullable=True),
        sa.Column('location_full', sa.Text(), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('experience_level', sa.String(length=100), nullable=True),
        sa.Column('source_platform', sa.String(length=100), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('crawled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_url')
    )
    op.create_index(op.f('ix_jobs_title'), 'jobs', ['title'], unique=False)
    op.create_index(op.f('ix_jobs_company_name'), 'jobs', ['company_name'], unique=False)
    op.create_index(op.f('ix_jobs_company_id'), 'jobs', ['company_id'], unique=False)
    op.create_index(op.f('ix_jobs_location_province'), 'jobs', ['location_province'], unique=False)
    op.create_index(op.f('ix_jobs_job_type'), 'jobs', ['job_type'], unique=False)
    op.create_index(op.f('ix_jobs_category'), 'jobs', ['category'], unique=False)
    op.create_index(op.f('ix_jobs_source_platform'), 'jobs', ['source_platform'], unique=False)
    op.create_index(op.f('ix_jobs_source_url'), 'jobs', ['source_url'], unique=True)
    op.create_index(op.f('ix_jobs_posted_at'), 'jobs', ['posted_at'], unique=False)
    op.create_index(op.f('ix_jobs_expires_at'), 'jobs', ['expires_at'], unique=False)
    op.create_index(op.f('ix_jobs_is_active'), 'jobs', ['is_active'], unique=False)


def downgrade() -> None:
    op.drop_table('jobs')
    op.drop_table('provinces')
    op.drop_table('companies')
