# Ask Your Database
A FastAPI backend that converts English into SQL and runs it on any connected Postgres (Supabase, Neon, Render, etc.)

This backend lets users:

✔ Connect their own database
✔ Automatically detect tables & columns
✔ Generate SQL from natural language
✔ Run SQL safely and return JSON
✔ Save / load custom schemas
✔ Support multiple projects (each with their own DB)


# ✨ Features

| Feature                              | Description                                                              |
| ------------------------------------ | ------------------------------------------------------------------------ |
| 🔌 **/connect**                      | Connect any Postgres DB (Supabase, Neon, AWS RDS, Render Postgres, etc.) |
| 🧠 **Automatic Schema Detection**    | Scans DB tables & columns using SQLAlchemy inspector                     |
| 💬 **Natural-Language Querying**     | “Show me expenses last 7 days” → SQL                                     |
| ➕ **Multi-project Engine Isolation** | Each project has its own DB engine + schema                              |
| 💾 **Schema Persistence**            | Saves schema inside user DB (table: `nlb_schemas`)                       |
| ⚙️ **Low-Code & Extensible**         | You can replace NLP engine whenever you want                             |


# 🏗️ Architecture Overview
```
                           ┌──────────────────────────┐
                           │        Dashboard UI       │
                           │  (React / Next.js / Vercel)│
                           └───────────┬──────────────┘
                                       │ REST API
                        ┌──────────────┴────────────────────┐
                        │        FastAPI Backend             │
                        │    (Render / Railway / Local)      │
┌───────────────────────┴────────────────────────────────────┴───────────────────┐
│                                Core Modules                                     │
│                                                                                 │
│ connections.py → stores DB URLs per project                                     │
│ schema_manager.py → manages schema per project                                  │
│ nlp_engine.py → converts natural language → parsed intent                       │
│ query_builder.py → converts parsed intent → SQL                                 │
│ db.py → executes SQL on correct engine                                          │
│ server.py → exposes API routes                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```


# 
🛠️ 1. Installation
Clone the repo
```
git clone https://github.com/yourname/natural-language-backend
```

```
cd natural-language-backend
```

Create & activate virtual environment

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```


If you don’t have requirements.txt, generate one:

```
pip freeze > requirements.txt
```

# ⚙️ 2. Environment Variables

Create .env:

# This DB is only for storing project metadata (connections + schemas)
DATABASE_URL=postgresql://YOUR_NEON_URL

-->
https://console.neon.tech/

This is NOT the client DB.

This DB only stores:

nlb_connections

nlb_schemas

Client databases stay separate.

# ▶️ 3. Start the FastAPI Server
```uvicorn app.server:app --reload
```

# Open interactive docs:

```
 http://127.0.0.1:8000/docs
```
```
http://127.0.0.1:8000/redoc
```

# 🔌 4. API Usage Guide (VERY IMPORTANT)
4.1 Connect your own database

This stores the DB URL and creates a dedicated SQLAlchemy engine.

POST /connect

Request
```
{
  "project": "eventplanner",
  "database_url": "postgresql://USER:PASSWORD@HOST:5432/postgres"
}
```

Response

{
  "status": "connected",
  "project": "eventplanner",
  "schema": {
    "status": "autodetected",
    "entities": ["events", "expenses", "profiles", ...]
  }
}

4.2 Run natural language queries
POST /query
```
{
  "project": "eventplanner",
  "text": "show me all profiles created last 7 days"
}
```

Response

{
  "parsed": {
    "entity": "profiles",
    "filter": "created_at >= NOW() - INTERVAL '7 days'"
  },
  "sql": "SELECT * FROM profiles WHERE created_at >= NOW() - INTERVAL '7 days' LIMIT 100",
  "result": [
    { ... rows returned ... }
  ]
}

4.3 Optional Schema Management

| Endpoint                    | Purpose                        |
| --------------------------- | ------------------------------ |
| **POST /schema**            | Manually upload schema         |
| **POST /schema/save**       | Save schema to DB              |
| **POST /schema/load**       | Load schema from DB            |
| **POST /schema/autodetect** | Re-scan DB and generate schema |
| **GET /schema/list**        | List all saved schemas         |


# Example Queries Users Can Try

| Natural Language                           | Generated SQL                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------ |
| “show me all profiles created last 7 days” | `SELECT * FROM profiles WHERE created_at >= NOW() - INTERVAL '7 days'`                     |
| “total expenses this month”                | `SELECT SUM(expenses.amount) FROM expenses WHERE created_at >= date_trunc('month', now())` |
| “count events in last 30 days”             | `SELECT COUNT(*) FROM events WHERE created_at >= NOW() - INTERVAL '30 days'`               |


# Limitations (Current v0)

1. NLP is basic keyword-based (not LLM yet)
2. No joins yet
3. No column type inference beyond names
4. No role-based access control
5. Aggregations require explicit numeric field detection
6. But for v0, this is already a working multi-project NL2SQL engine.

