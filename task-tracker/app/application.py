from collections.abc import Callable
from types import ModuleType
from typing import cast

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from app.settings import Settings


class Application(FastAPI):
    def __init__(self, settings: Settings, on_startup: list[Callable]) -> None:
        self.settings = settings
        super().__init__(
            title=settings.PROJECT_NAME,
            description=settings.DESCRIPTION,
            version=settings.VERSION,
            debug=settings.DEBUG,
            openapi_url='/srv/openapi.json',
            docs_url='/srv/docs',
            redoc_url='/srv/redoc',
            swagger_ui_oauth2_redirect_url='/srv/docs/oauth2-redirect',
            on_startup=on_startup,
        )

    def build_middleware_stack(self) -> ASGIApp:
        return CORSMiddleware(
            app=super().build_middleware_stack(),
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            allow_origin_regex=self.settings.ORIGIN_REGEX,
        )

    def register_endpoints(self, *modules: ModuleType) -> None:
        for module in modules:
            self.include_router(cast(APIRouter, module.router))
