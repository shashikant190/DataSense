# app/server.py

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.connections import ConnectRequest, save_connection, connect_project_engine
from app.schema_manager import (
    set_schema, get_schema, save_schema,
    load_schema, autodetect_schema, get_engine
)
from app.db import run_sql
from app.nlp_engine import parse_query
from app.query_builder import build_sql

load_dotenv()

# IMPORTANT: add both GitHub Pages and localhost
allowed_origins = [
    os.getenv("FRONTEND_ORIGIN", "https://shashikant190.github.io"),
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

class QueryRequest(BaseModel):
    text: str
    project: str = "default"


@app.post("/connect")
def connect_db(req: ConnectRequest):
    save_connection(req.project, req.database_url)
    connect_project_engine(req.project, req.database_url)
    detected = autodetect_schema(req.project)

    return {
        "status": "connected",
        "project": req.project,
        "schema": detected
    }


@app.post("/schema")
def upload_schema(data: dict, project: str = "default"):
    return set_schema(data, project)


@app.post("/schema/save")
def save_schema_endpoint(project: str = "default"):
    return save_schema(project)


@app.post("/schema/load")
def load_schema_endpoint(project: str = "default"):
    return load_schema(project)


@app.post("/schema/autodetect")
def autodetect_endpoint(project: str = "default"):
    return autodetect_schema(project)


@app.post("/query")
def query_endpoint(req: QueryRequest):

    schema = get_schema(req.project)
    if not schema:
        raise HTTPException(400, "Schema not loaded. POST /schema or /schema/load first.")

    engine = get_engine(req.project)
    parsed = parse_query(req.text, schema)

    if not parsed.get("entity"):
        raise HTTPException(400, f"Could not identify entity from: {req.text}")

    sql = build_sql(parsed)
    result = run_sql(sql, engine=engine)

    return {"parsed": parsed, "sql": sql, "result": result}
