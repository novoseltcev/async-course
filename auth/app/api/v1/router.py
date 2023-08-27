from fastapi import APIRouter

from .accounts.endpoint import router as account_router
from .auth import router as auth_router

router = APIRouter(prefix='/v1', tags=['V1'])
router.include_router(account_router, prefix='/accounts')
router.include_router(auth_router, prefix='/auth')
