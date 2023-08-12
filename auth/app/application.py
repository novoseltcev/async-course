from types import ModuleType
from typing import cast

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import Settings


class Application(FastAPI):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        super().__init__(
            title=settings.PROJECT_NAME,
            description=settings.DESCRIPTION,
            version=settings.VERSION,
            debug=settings.DEBUG,
        )

        self.add_middleware(
            CORSMiddleware,
            allow_origin_regex=settings.ORIGIN_REGEX,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

    def register_endpoints(self, *modules: ModuleType) -> None:
        for module in modules:
            self.include_router(cast(APIRouter, module.router))
