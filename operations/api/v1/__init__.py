from fastapi import APIRouter

from . import ss, tax, users

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(ss.router, prefix="/social-security", tags=["Social Security"])
router.include_router(tax.router, prefix="/tax", tags=["Tax"])
