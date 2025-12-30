from fastapi import APIRouter

from . import auth, ss, tax, users

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(ss.router, prefix="/social-security", tags=["Social Security"])
router.include_router(tax.router, prefix="/tax", tags=["Tax"])
