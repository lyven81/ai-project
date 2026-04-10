"""
AI Agent + Database Template — FastAPI REST API
Agent converts natural language to SQL queries automatically.
Supports SQLite (local) and PostgreSQL/AlloyDB (cloud).
Edit config.yaml to customize for your business.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, re, yaml, sqlite3, csv
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ── Load config ──────────────────────────────────────────────────────
with open("config.yaml", "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

BIZ = CFG["business_name"]
CURRENCY = CFG.get("currency", "RM")
DB_CFG = CFG.get("database", {})
DB_MODE = DB_CFG.get("mode", "sqlite")
SCHEMA = DB_CFG.get("schema", "")

# ── API setup ────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY and GOOGLE_API_KEY != "placeholder_key_to_update":
    genai.configure(api_key=GOOGLE_API_KEY)
    API_CONFIGURED = True
else:
    API_CONFIGURED = False

app = FastAPI(title=f"{BIZ} Analytics Agent (Database)", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    status: str
    sql_query: str = ""
    rows_returned: int = 0


# ── Database connection ──────────────────────────────────────────────

def get_sqlite_conn():
    return sqlite3.connect(DB_CFG.get("sqlite_file", "data.db"))


def get_pg_conn():
    try:
        import psycopg2
    except ImportError:
        raise RuntimeError("Install psycopg2: pip install psycopg2-binary")
    password = os.getenv(DB_CFG.get("password_env", "DB_PASSWORD"), "")
    return psycopg2.connect(
        host=DB_CFG.get("host", "localhost"),
        port=DB_CFG.get("port", 5432),
        dbname=DB_CFG.get("dbname", "analytics"),
        user=DB_CFG.get("user", "postgres"),
        password=password,
    )


def get_conn():
    if DB_MODE == "sqlite":
        return get_sqlite_conn()
    return get_pg_conn()


def execute_sql(sql):
    """Execute a SELECT query and return results."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return {"columns": columns, "rows": rows, "count": len(rows)}
    finally:
        conn.close()


def get_row_count():
    """Get total row count from the main table."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        # Extract table name from schema
        table_match = re.search(r"Table:\s*(\w+)", SCHEMA)
        table = table_match.group(1) if table_match else "orders"
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]
    except Exception:
        return 0
    finally:
        conn.close()


# ── CSV Import (SQLite only) ─────────────────────────────────────────

def import_csv_to_sqlite():
    """Import CSV file into SQLite on first run."""
    csv_file = DB_CFG.get("csv_import", "")
    db_file = DB_CFG.get("sqlite_file", "data.db")
    if not csv_file or not os.path.exists(csv_file):
        return
    if os.path.exists(db_file) and os.path.getsize(db_file) > 0:
        return

    # Extract table name from schema
    table_match = re.search(r"Table:\s*(\w+)", SCHEMA)
    table_name = table_match.group(1) if table_match else "orders"

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table with TEXT columns (SQLite is flexible with types)
    col_defs = ", ".join(f'"{c}" TEXT' for c in columns)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})")

    # Insert rows
    placeholders = ", ".join("?" for _ in columns)
    col_names = ", ".join(f'"{c}"' for c in columns)
    for row in rows:
        values = [row.get(c, "") for c in columns]
        cursor.execute(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()


# ── Build prompt ─────────────────────────────────────────────────────

PROMPT_TEMPLATE = """You are {biz} analytics agent. You answer business questions by writing SQL queries.

Database schema:
{schema}

Currency: {currency}
Database type: {db_mode}

INSTRUCTIONS:
1. Read the user's question carefully.
2. Write a SQL SELECT query that answers the question.
3. Output the SQL in a ```sql code block.
4. After the SQL block, write a brief summary of the results in plain English.
5. Only write SELECT queries. Never write INSERT, UPDATE, DELETE, DROP, or ALTER.
6. Use standard SQL. For dates, use text comparison (e.g., order_date >= '2024-01-01').
7. Limit results to 20 rows unless the user asks for more.
8. Use aliases for calculated columns (e.g., SUM(total_amount) AS total_sales).

Sample questions this system can answer:
{sample_questions}

User question: {{question}}"""

PROMPT = PROMPT_TEMPLATE.format(
    biz=BIZ,
    schema=SCHEMA,
    currency=CURRENCY,
    db_mode=DB_MODE,
    sample_questions="\n".join(f"- {q}" for q in DB_CFG.get("sample_questions", [])),
)


# ── Code generation ──────────────────────────────────────────────────

def generate_sql(question):
    if not API_CONFIGURED:
        raise HTTPException(500, "API key not configured. Set GOOGLE_API_KEY in .env")
    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config=genai.GenerationConfig(temperature=0.0),
    )
    response = model.generate_content(PROMPT.format(question=question))
    return response.candidates[0].content.parts[0].text if response.candidates else ""


def extract_sql(text):
    m = re.search(r"```sql\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def is_safe_sql(sql):
    """Block anything that isn't a read-only SELECT or CTE (WITH ... SELECT)."""
    upper = sql.upper().strip().rstrip(";").strip()
    # Allow both plain SELECT and WITH...SELECT (common pattern for complex queries)
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False
    # Word-boundary check so 'created_at' doesn't trip 'CREATE'
    dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "EXEC", "REPLACE", "ATTACH"]
    for keyword in dangerous:
        if re.search(r"\b" + keyword + r"\b", upper):
            return False
    return True


def format_results(columns, rows, currency="RM"):
    """Format query results as a markdown table."""
    if not rows:
        return "No results found."
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows[:20]:
        cells = []
        for val in row:
            if val is None:
                cells.append("—")
            elif isinstance(val, float):
                cells.append(f"{val:,.2f}")
            else:
                cells.append(str(val))
        lines.append("| " + " | ".join(cells) + " |")
    if len(rows) > 20:
        lines.append(f"\n*Showing first 20 of {len(rows)} results.*")
    return "\n".join(lines)


# ── API endpoints ────────────────────────────────────────────────────

@app.get("/")
async def root():
    return FileResponse("demo.html")


@app.get("/api/status")
async def status():
    row_count = get_row_count()
    return {
        "message": f"{BIZ} Analytics Agent (Database)",
        "version": "1.0.0",
        "database_mode": DB_MODE,
        "records": row_count,
        "api_configured": API_CONFIGURED,
        "status": "API key required" if not API_CONFIGURED else "Ready",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Step 1: Generate SQL
        raw = generate_sql(request.message)
        sql = extract_sql(raw)
        if not sql:
            return ChatResponse(
                answer="I couldn't generate a query for that question. Try rephrasing it.",
                status="error", sql_query="", rows_returned=0,
            )

        # Step 2: Safety check
        if not is_safe_sql(sql):
            return ChatResponse(
                answer="That query type is not allowed. I can only run SELECT queries.",
                status="error", sql_query=sql, rows_returned=0,
            )

        # Step 3: Execute SQL
        result = execute_sql(sql)

        # Step 4: Format results
        table = format_results(result["columns"], result["rows"], CURRENCY)
        answer = f"**Query Results:**\n\n{table}"

        return ChatResponse(
            answer=answer,
            status="success",
            sql_query=sql,
            rows_returned=result["count"],
        )
    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(
            answer=f"Error running query: {str(e)}",
            status="error", sql_query="", rows_returned=0,
        )


@app.get("/api/config")
async def get_config():
    row_count = get_row_count()
    return {
        "business_name": BIZ,
        "tagline": CFG.get("tagline", ""),
        "currency": CURRENCY,
        "dataset": {
            "description": f"Database ({DB_MODE})",
            "records": row_count,
            "date_range": {"from": "", "to": ""},
        },
        "database_mode": DB_MODE,
        "demo": CFG.get("demo", {}),
    }


@app.on_event("startup")
async def startup():
    if DB_MODE == "sqlite":
        import_csv_to_sqlite()


if __name__ == "__main__":
    import uvicorn
    port = CFG.get("deployment", {}).get("port", 8080)
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", port)))
