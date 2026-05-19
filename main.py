from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import sqlite3
import random
import string

app = FastAPI()
DB_NAME = "urls.db"
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
                 short_code TEXT PRIMARY KEY,
                 long_url TEXT NOT NULL,
                 click_count INTEGER DEFAULT 0,
                 created_at TEXT NOT NULL
                 )
    """)
    conn.commit()
    conn.close()


# Temporary in-memory 'database'
url_store = {}

class CreateUrlRequest(BaseModel):
    longUrl: HttpUrl

def generate_short_code(length: int=6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

@app.get("/")           # when a client sends an HTTP GET request to /, run this Python function.
def health_check():
    return{"message": "URL shortener API is running"}

@app.post("/urls")      # when a client sends an HTTP POST request to /urls, run this Python function.
def create_short_url(request: CreateUrlRequest):
    short_code = generate_short_code()

    created_at = datetime.utcnow().isoformat()
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO urls (short_code, long_url, click_count, created_at) VALUES (?, ?, ?, ?)",
        (short_code, str(request.longUrl), 0, created_at)
    )
    conn.commit()
    conn.close()


    return {
            "shortCode": short_code,
            "shortUrl": f"http://127.0.0.1:8000/{short_code}",
            "longUrl": str(request.longUrl)
            }

@app.get("/debug/urls")
def debug_urls():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM urls").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/{short_code}")   # when a client sends an HTTP GET request to /{short_code}, run this Python function.
                            # this one should always be defined later, because it is a wildcard route, and if it is before the other routes, it will catch all requests and the other routes will never be reached.
def redirect_to_long_url(short_code: str):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    conn.execute(
        "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
        (short_code,)
    )
    conn.commit()
    conn.close()

    return RedirectResponse(url=row["long_url"], status_code=302)