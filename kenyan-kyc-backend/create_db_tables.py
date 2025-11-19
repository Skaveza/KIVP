# create_db_tables.py
"""
One-off script to create all database tables based on SQLAlchemy models.

Run from project root:
    (venv) $ python create_db_tables.py
"""

from app.core.database import Base, engine
from app.models import models  # ensure all model classes are imported


def init_db():
    # This will create all tables defined on Base's metadata
    Base.metadata.create_all(bind=engine)
    print(" All tables created (if they didn't already exist).")


if __name__ == "__main__":
    init_db()
