from fastapi import APIRouter, Request

from core.templating.utils import render

routers = APIRouter(tags=["chat"], prefix="/chat")


@routers.get("/")
def chat(request: Request):
    return render(request, "chat/index.html")
