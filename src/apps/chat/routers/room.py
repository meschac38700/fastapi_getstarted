from fastapi import APIRouter, Request

routers = APIRouter()


@routers.get("/")
def chat(_: Request):
    return {"status": "Coming soon"}
