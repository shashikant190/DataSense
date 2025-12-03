# app/db.py
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, future=True)


def run_sql(sql, engine=None, params=None):
    if engine is None:
        from app.db import engine as default_engine
        engine = default_engine

    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        rows = result.mappings().all()
    return rows
