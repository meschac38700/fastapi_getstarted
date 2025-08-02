from fastapi import FastAPI
from fastapi.openapi import utils as openapi_utils


def custom_openapi(app: FastAPI):
    def _custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = openapi_utils.get_openapi(
            title="FastApi starter",
            version="0.0.4",
            summary="FastApi starter - Python base Api application",
            description="""
This web application serves as a starter kit for building robust APIs using
the FastAPI framework. It provides a foundational structure that includes
built-in authentication, a permission management system, and other useful features.
The goal is to offer developers a streamlined starting point,
simplifying the initial setup and promoting a better development experience.
            """,
            routes=app.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = _custom_openapi
