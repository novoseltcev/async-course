from fastapi import APIRouter

from .services import router as services_router
from .sso import router as sso_router

router = APIRouter(prefix='/srv', tags=['SRV'])
router.include_router(sso_router, prefix='/sso')
router.include_router(services_router, prefix='/services')
