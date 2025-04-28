from fastapi import APIRouter
from App.publicdata.schoolinfo.public_schoolinfo_router import router as public_schoolinfo_router
from App.publicdata.schoolinfo.private_schoolinfo_router import router as private_schoolinfo_router
from App.publicdata.schoolinfo.schoolinfo_batch_router import router as schoolinfo_batch_router

router = APIRouter(
    prefix="/publicdata",
    tags=["Public Data"],
)

router.include_router(public_schoolinfo_router)
router.include_router(private_schoolinfo_router)
router.include_router(schoolinfo_batch_router)