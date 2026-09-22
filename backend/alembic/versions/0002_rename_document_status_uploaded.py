"""rename document status: pending -> uploaded

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-22

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CHECK_NAME = "ck_documents_status"
STATUSES_PROCESSING = ["processing", "processed", "failed"]


def upgrade() -> None:
    op.execute(f"ALTER TABLE documents DROP CONSTRAINT IF EXISTS {CHECK_NAME}")
    op.execute(
        "UPDATE documents SET status = 'uploaded' WHERE status = 'pending'"
    )
    allowed = ", ".join(repr(s) for s in ["uploaded", *STATUSES_PROCESSING])
    op.execute(
        f"ALTER TABLE documents ADD CONSTRAINT {CHECK_NAME} "
        f"CHECK (status IN ({allowed}))"
    )
    op.execute("ALTER TABLE documents ALTER COLUMN status SET DEFAULT 'uploaded'")


def downgrade() -> None:
    op.execute(f"ALTER TABLE documents DROP CONSTRAINT IF EXISTS {CHECK_NAME}")
    op.execute(
        "UPDATE documents SET status = 'pending' WHERE status = 'uploaded'"
    )
    allowed = ", ".join(repr(s) for s in ["pending", *STATUSES_PROCESSING])
    op.execute(
        f"ALTER TABLE documents ADD CONSTRAINT {CHECK_NAME} "
        f"CHECK (status IN ({allowed}))"
    )
    op.execute("ALTER TABLE documents ALTER COLUMN status SET DEFAULT 'pending'")