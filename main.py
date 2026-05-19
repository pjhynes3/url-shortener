from fastapi import FastAPI
from pydantic import BaseModel
import random
import string

app = FastAPI()

# Temporary in-memory 'database'
url_store = {}

class CreateUrlRequest(BaseModel):
    longUrl: str

def generate_short_code(length: int=6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

@app.get("/")           # when a client sends an HTTP GET request to /urls, run this Python function.
def health_check():
    return{"message": "URL shortener API is running"}

@app.post("/urls")      # when a client sends an HTTP POST request to /urls, run this Python function.
def create_short_url(request: CreateUrlRequest):
    short_code = generate_short_code()

    url_store[short_code] = request.longUrl

    return {
            "shortCode": short_code,
            "shortUrl": f"http://127.0.0.1:8000/{short_code}",
            "longUrl": request.longUrl
            }
