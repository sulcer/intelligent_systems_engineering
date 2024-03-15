from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def health_check():
    return {"status": "api is up and running"}
