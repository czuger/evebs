"""Add industry_taxes JSONB column to users.

Stores per-user EVE Online industry tax configuration as a JSONB object.
One top-level key per activity type; each key holds the three cost components
that multiply against the job's estimated item value (EIV) on the blueprint:

  system_cost_index  — set by CCP per solar system based on industrial activity
                       in that system; queried from ESI /industry/systems/.
                       Example: 0.05 means the system charges 5 % of EIV.

  scc_tax            — Secure Commerce Commission flat surcharge applied on top
                       of the system cost index for all industry jobs.
                       Typically 1.5 % (CCP-set, varies with patch notes).

  Activity-specific taxes (vary by what the player's structure owner charges):
    manufacturing  → standard_tax  (normal manufacturing jobs)
                     capital_tax   (capital ship / capital component jobs)
    copying        → copying_tax
    invention      → invention_tax
    material_research → material_tax  (ME research)
    time_research     → time_tax      (TE research)
    reaction          → reaction_tax

All values are stored as PLAIN PERCENTAGES (e.g. 5.0 means 5 %, NOT 0.05).
Divide by 100 before multiplying against ISK amounts in calculations.

The server_default backfills all pre-existing rows with the typical values
a player would see at an NPC station in a quiet high-sec system:
  system_cost_index = 5 %   (representative high-sec average)
  scc_tax           = 4 %   (CCP default as of 2024)
  activity taxes    = 1 %   (NPC station flat rate)

Revision ID: c5cdf79f0952
Revises: cb2263e81cf3
Create Date: 2026-06-05 19:53:55.059320
"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c5cdf79f0952'
down_revision: Union[str, None] = 'cb2263e81cf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mirror of User.industry_taxes default — keep in sync with user.py.
_DEFAULT = {
    'manufacturing':     {'system_cost_index': 5.0, 'scc_tax': 4.0, 'standard_tax': 1.0, 'capital_tax': 1.0},
    'material_research': {'system_cost_index': 5.0, 'scc_tax': 4.0, 'material_tax': 1.0},
    'time_research':     {'system_cost_index': 5.0, 'scc_tax': 4.0, 'time_tax': 1.0},
    'copying':           {'system_cost_index': 5.0, 'scc_tax': 4.0, 'copying_tax': 1.0},
    'invention':         {'system_cost_index': 5.0, 'scc_tax': 4.0, 'invention_tax': 1.0},
    'reaction':          {'system_cost_index': 5.0, 'scc_tax': 4.0, 'reaction_tax': 1.0},
}


def upgrade() -> None:
    # server_default ensures existing rows are backfilled immediately;
    # new rows created via the ORM use the Python-level default in user.py.
    op.add_column('users', sa.Column(
        'industry_taxes',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text(f"'{json.dumps(_DEFAULT)}'::jsonb"),
    ))


def downgrade() -> None:
    op.drop_column('users', 'industry_taxes')
