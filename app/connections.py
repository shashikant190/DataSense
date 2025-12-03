# app/connections.py
from sqlalchemy import text, create_engine
from pydantic import BaseModel
from app.db import engine as main_engine
from app.schema_manager import set_engine


class ConnectRequest(BaseModel):
    project: str
    database_url: str


def save_connection(project: str, db_url: str):
    # Save connection in the metadata DB (local)
    with main_engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS nlb_connections (
                project_name TEXT PRIMARY KEY,
                db_url TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))

        conn.execute(text("""
            INSERT INTO nlb_connections (project_name, db_url)
            VALUES (:project, :db_url)
            ON CONFLICT(project_name) DO UPDATE SET db_url = EXCLUDED.db_url;
        """), {"project": project, "db_url": db_url})


def connect_project_engine(project: str, url: str):
    engine = create_engine(url, future=True)
    set_engine(project, engine)
    return engine
