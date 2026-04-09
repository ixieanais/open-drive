import os
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, File, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

import config
from database import crud
from schemas import FileSchema


router = APIRouter(tags=["files"])


@router.post("/folders/{folder_id}/files")
async def upload_files(folder_id: str, files: list[UploadFile] = File(...)):
    for file in files:
        file_id = str(uuid4())
        mime_type = file.content_type

        try:
            async with aiofiles.open(config.STORAGE_DIR / file_id, "wb") as f:
                while chunk := await file.read(1024 * 1024):
                    await f.write(chunk)

            split_filename = file.filename.split(".")
            filename = f"{split_filename[0][0 : 50 - (len(split_filename[-1]) + 1)]}.{split_filename[-1]}"

            await crud.insert_file(
                id=file_id,
                filename=filename,
                mime_type=mime_type,
                type=file.filename.split(".")[-1],
                size=file.size,
                folder_id=folder_id,
            )

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The file ({filename}) exists",
            )

    return {"detail": "Done"}


@router.get("/folders/{folder_id}/files")
async def search_files(folder_id: str):
    return await crud.select_files(folder_id)


@router.get("/files/{file_id}/download")
async def download_files(file_id: str):
    try:
        file = await crud.select_file(file_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    path = config.STORAGE_DIR / file_id
    return FileResponse(
        path=path, media_type="application/octet-stream", filename=file["filename"]
    )


@router.get("/files/search")
async def get_files_from_search(query: str):
    return await crud.select_similar_files(query)


@router.get("/files/{file_id}")
async def get_file(file_id: str):
    try:
        file = await crud.select_file(file_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The file doesn't exist"
        )

    file_type = file["type"]

    return FileResponse(config.STORAGE_DIR / file_id, media_type=file_type)


@router.get("/files/{file_id}/meta")
async def get_file_metadata(file_id: str):
    return await crud.select_file(file_id)


@router.patch("/files/{file_id}")
async def update_file(file_id: str, schema: FileSchema):
    print(schema.name, schema.folder_id)
    if schema.name and schema.folder_id is None:
        await crud.update_filename(file_id, schema.name)
    elif schema.folder_id and schema.name is None:
        await crud.update_file_location(file_id, schema.folder_id)


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    file_path = config.STORAGE_DIR / file_id
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The file doesn't exist"
        )

    os.remove(file_path)

    await crud.delete_file(file_id)
