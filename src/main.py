import secrets

from fastapi import FastAPI

app = FastAPI()


@app.get("/", name="Generate secret key.")
def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}
