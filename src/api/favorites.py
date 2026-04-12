from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from database import crud


router = APIRouter(tags=["favorites"])


@router.post("/favorites/{folder_id}")
async def create_favorite(folder_id: str):
    try:
        await crud.insert_favorite(folder_id)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.get("/favorites")
async def get_favorites():
    return await crud.select_favorites()


# @router.patch("/favorites/{folder_id}")
# async def update_favorite(folder_id: str):
#     pass


@router.delete("/favorites/{folder_id}")
async def delete_favorite(folder_id: str):
    await crud.delete_favorite(folder_id)
