from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import random
import string

app = FastAPI()

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

    url_store[short_code] = {
        "long_url": request.longUrl,
        "click_count": 0,
        "created_at": datetime.utcnow().isoformat()
    }


    return {
            "shortCode": short_code,
            "shortUrl": f"http://127.0.0.1:8000/{short_code}",
            "longUrl": request.longUrl
            }

@app.get("/debug/urls")
def debug_urls():
    return url_store

@app.get("/{short_code}")   # when a client sends an HTTP GET request to /{short_code}, run this Python function.
                            # this one should always be defined later, because it is a wildcard route, and if it is before the other routes, it will catch all requests and the other routes will never be reached.
def redirect_to_long_url(short_code: str):
    if short_code not in url_store:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    url_store[short_code]["click_count"] += 1
    long_url = url_store[short_code]["long_url"]
    return RedirectResponse(url=long_url, status_code=302)