from fastapi import APIRouter

router = APIRouter(
    prefix="/publicdata",
    tags=["PublicData"]
)

@router.post("/raw")
def collect_publicdata_raw():
    return {"message": "Public data raw collection endpoint"}
