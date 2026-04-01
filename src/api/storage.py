import asyncio
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

import config
from database import crud
from schemas import FileSchema, FolderSchema


router = APIRouter()


def zip_to_file(files, path):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as z:
        for file in files:
            z.write(config.STORAGE_DIR / file["id"], arcname=file["filename"])


async def get_files_from_folders(data: list, folder_id: str):
    files = await crud.select_files(folder_id)
    data.extend(files)
    folders = await crud.select_folders(folder_id)
    if folders:
        for folder in folders:
            await get_files_from_folders(data, folder["id"])

    return data


@router.post("/folders/{folder_id}/files", tags=["files"])
async def upload_files(folder_id: str, files: list[UploadFile] = File(...)):
    for file in files:
        file_id = str(uuid4())

        try:
            await crud.insert_file(
                id=file_id,
                filename=file.filename,
                mime_type=file.content_type,
                type=file.filename.split(".")[-1],
                size=file.size,
                folder_id=folder_id,
            )

            async with aiofiles.open(config.STORAGE_DIR / file_id, "wb") as f:
                content = await file.read()
                await f.write(content)

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The file ({file_id}) exists",
            )

    return {"detail": "Done"}


@router.get("/folders/{folder_id}/files", tags=["files"])
async def search_files(folder_id: str):
    return await crud.select_files(folder_id)


@router.get("/files/{file_id}/download", tags=["files"])
async def download_files(file_id: str):
    try:
        file = await crud.select_file(file_id)
        path = config.STORAGE_DIR / file_id
        return FileResponse(
            path=path, media_type="application/octet-stream", filename=file["filename"]
        )
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/files/search", tags=["files"])
async def get_files_from_search(query: str):
    return await crud.select_similar_files(query)


@router.get("/files/{file_id}", tags=["files"])
async def get_file(file_id: str):
    file = await crud.select_file(file_id)
    file_type = file["type"]

    if file:
        return FileResponse(config.STORAGE_DIR / file_id, media_type=file_type)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="The file doesn't exist"
    )


@router.get("/files/{file_id}/meta", tags=["files"])
async def get_file_metadata(file_id: str):
    return await crud.select_file(file_id)


@router.patch("/files/{file_id}", tags=["files"])
async def update_filename(file_id: str, schema: FileSchema):
    await crud.update_filename(file_id, schema.name)


@router.delete("/files/{file_id}", tags=["files"])
async def delete_file(file_id: str):
    try:
        os.remove(config.STORAGE_DIR / file_id)
        await crud.delete_file(file_id)
        return {"detail": "Done"}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The file doesn't exist"
        )


@router.post("/folders/{parent_id}", tags=["folders"])
async def create_folder(parent_id: str, schema: FolderSchema):
    parent_folder = await crud.select_folder(parent_id)
    parent_path = parent_folder["path"]
    new_path = f"{parent_path}/{schema.name}"

    try:
        id = str(uuid4())
        await crud.insert_folder(id, new_path, parent_id)
        return id
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The folder is exists"
        )


@router.get("/folders/main", tags=["folders"])
async def get_main_folder():
    folder_id = await crud.select_folder_id("/home")
    return await crud.select_folder(folder_id)


@router.get("/folders/search", tags=["folders"])
async def search_folders(query: Optional[str] = None, path: Optional[str] = None):
    if query:
        return await crud.select_similar_folders(query)

    if path:
        try:
            folder_id = await crud.select_folder_id(path)
            return await crud.select_folder(folder_id)

        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/folders/{parent_id}", tags=["folders"])
async def get_folders(parent_id: str):
    return await crud.select_folders(parent_id)


@router.get("/folders/{folder_id}/files/total", tags=["folders"])
async def get_folder_total_files(folder_id: str):
    files = await get_files_from_folders(list(), folder_id)
    return len(files)


@router.get("/folders/{folder_id}/metadata", tags=["folders"])
async def get_folder_metadata(folder_id: str):
    return await crud.select_folder(folder_id)


@router.get("/folders/{folder_id}/download", tags=["folders"])
async def download_folders_as_archive(bg_tasks: BackgroundTasks, folder_id: str):
    files = await get_files_from_folders(list(), folder_id)
    folder = await crud.select_folder(folder_id)
    folder_name = folder["path"].split("/")[-1]

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    path = Path(tmp.name)
    tmp.close()

    await asyncio.to_thread(zip_to_file, files, path)

    bg_tasks.add_task(os.remove, path)

    return FileResponse(path=path, filename=f"{folder_name}.zip")


@router.patch("/folders/{folder_id}", tags=["folders"])
async def update_folder(folder_id: str, schema: FolderSchema):
    folder = await crud.select_folder(folder_id)
    path = folder["path"]

    new_path = path.replace(path.split("/")[-1], schema.name)

    await crud.update_folder(folder_id, new_path)


@router.delete("/folders/{folder_id}", tags=["folders"])
async def delete_folder(folder_id: str):
    folders = await crud.select_folders(folder_id)
    for folder in folders:
        await delete_folder(folder["id"])

    files = await crud.select_files(folder_id)
    for file in files:
        file_path = config.STORAGE_DIR / file["id"]
        if file_path.exists():
            os.remove(file_path)

    await crud.delete_folder(folder_id)
