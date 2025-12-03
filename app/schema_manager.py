# app/schema_manager.py

import json
from typing import Dict, Any
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

active_schemas: Dict[str, Dict[str, Any]] = {}
active_engines: Dict[str, Engine] = {}

SCHEMA_TABLE = "nlb_schemas"


def set_engine(project: str, engine: Engine):
    active_engines[project] = engine


def get_engine(project: str):
    if project not in active_engines:
        raise ValueError(f"No engine for project '{project}'")
    return active_engines[project]


def set_schema(data: Dict[str, Any], project: str):
    active_schemas[project] = data
    return {"status": "schema loaded", "project": project}


def get_schema(project: str):
    return active_schemas.get(project, {})


def save_schema(project: str):
    engine = get_engine(project)
    schema = get_schema(project)

    if not schema:
        return {"error": "No active schema to save"}

    with engine.begin() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA_TABLE} (
                name TEXT PRIMARY KEY,
                schema_json TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))

        conn.execute(text(f"""
            INSERT INTO {SCHEMA_TABLE} (name, schema_json)
            VALUES (:name, :schema_json)
            ON CONFLICT(name) DO UPDATE SET schema_json = EXCLUDED.schema_json
        """), {"name": project, "schema_json": json.dumps(schema)})

    return {"status": "saved", "project": project}


def load_schema(project: str):
    engine = get_engine(project)

    with engine.connect() as conn:
        row = conn.execute(
            text(f"SELECT schema_json FROM {SCHEMA_TABLE} WHERE name = :name"),
            {"name": project}
        ).fetchone()

    if not row:
        return {"error": "Schema not found"}

    schema = json.loads(row[0])
    active_schemas[project] = schema

    return {"status": "loaded", "project": project, "schema": schema}


def autodetect_schema(project: str):
    engine = get_engine(project)
    insp = inspect(engine)

    entities = {}
    for table in insp.get_table_names():
        cols = insp.get_columns(table)
        entities[table] = {
            "fields": [c["name"] for c in cols],
            "synonyms": []
        }

    schema = {"entities": entities}
    active_schemas[project] = schema

    save_schema(project)

    return {
        "status": "autodetected",
        "project": project,
        "entities": list(entities.keys())
    }
