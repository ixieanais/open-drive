import asyncio
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

import config
from database import crud
from schemas import FolderSchema


router = APIRouter(tags=["folders"])


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


@router.post("/folders/{parent_id}")
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


@router.get("/folders/main")
async def get_main_folder():
    folder_id = await crud.select_folder_id("/home")
    return await crud.select_folder(folder_id)


@router.get("/folders/search")
async def search_folders(query: Optional[str] = None, path: Optional[str] = None):
    if query:
        return await crud.select_similar_folders(query)

    if path:
        try:
            folder_id = await crud.select_folder_id(path)
            return await crud.select_folder(folder_id)

        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/folders/{parent_id}")
async def get_folders(parent_id: str):
    return await crud.select_folders(parent_id)


@router.get("/folders/{folder_id}/files/total")
async def get_folder_total_files(folder_id: str):
    files = await get_files_from_folders(list(), folder_id)
    return len(files)


@router.get("/folders/{folder_id}/metadata")
async def get_folder_metadata(folder_id: str):
    return await crud.select_folder(folder_id)


@router.get("/folders/{folder_id}/download")
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


@router.patch("/folders/{folder_id}")
async def update_folder(folder_id: str, schema: FolderSchema):
    folder = await crud.select_folder(folder_id)
    path = folder["path"]

    new_path = path.replace(path.split("/")[-1], schema.name)

    await crud.update_folder(folder_id, new_path)


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str):
    folders = await crud.select_folders(folder_id)
    for folder in folders:
        await delete_folder(folder["id"])

    files = await crud.select_files(folder_id)
    for file in files:
        file_path = config.STORAGE_DIR / file["id"]
        if file_path.exists():
            os.remove(file_path)
            preview_path = config.STORAGE_DIR / f"{file['id']}.preview"
            if preview_path.exists():
                os.remove(preview_path)

    await crud.delete_folder(folder_id)
