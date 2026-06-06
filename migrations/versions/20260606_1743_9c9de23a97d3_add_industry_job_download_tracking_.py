"""add industry job download tracking columns to users

Revision ID: 9c9de23a97d3
Revises: 7fe8b1486ef5
Create Date: 2026-06-06 17:43:54.564676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9c9de23a97d3'
down_revision: Union[str, None] = '7fe8b1486ef5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS industry_jobs (
            id                     SERIAL PRIMARY KEY,
            user_id                BIGINT NOT NULL REFERENCES users(id),
            job_id                 BIGINT NOT NULL,
            installer_id           BIGINT,
            facility_id            BIGINT,
            station_id             BIGINT,
            activity_id            INTEGER NOT NULL,
            blueprint_id           BIGINT,
            blueprint_type_id      INTEGER,
            blueprint_location_id  BIGINT,
            output_location_id     BIGINT,
            runs                   INTEGER,
            cost                   DOUBLE PRECISION,
            licensed_runs          INTEGER,
            probability            DOUBLE PRECISION,
            product_type_id        INTEGER,
            status                 VARCHAR NOT NULL,
            duration               INTEGER,
            start_date             TIMESTAMP,
            end_date               TIMESTAMP,
            pause_date             TIMESTAMP,
            completed_date         TIMESTAMP,
            completed_character_id BIGINT,
            successful_runs        INTEGER,
            created_at             TIMESTAMP,
            updated_at             TIMESTAMP,
            CONSTRAINT uq_industry_jobs_user_job UNIQUE (user_id, job_id)
        )
    """))
    conn.execute(sa.text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS download_industry_jobs_running BOOLEAN NOT NULL DEFAULT FALSE"
    ))
    conn.execute(sa.text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_industry_jobs_download TIMESTAMP"
    ))


def downgrade() -> None:
    op.drop_table('industry_jobs')
    op.drop_column('users', 'last_industry_jobs_download')
    op.drop_column('users', 'download_industry_jobs_running')
