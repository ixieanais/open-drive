import json
import os
import subprocess
from uuid import uuid4

import aiofiles
from icoextract import IconExtractor, IconExtractorError
from fastapi import APIRouter, File, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from PIL import Image
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
        preview_exists = False

        try:
            async with aiofiles.open(config.STORAGE_DIR / file_id, "wb") as f:
                while chunk := await file.read(1024 * 1024):
                    await f.write(chunk)

            if mime_type.startswith("image/"):
                preview_exists = True
                with Image.open(config.STORAGE_DIR / file_id) as img:
                    img.thumbnail((512, 512))
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(config.STORAGE_DIR / f"{file_id}.preview", format="JPEG", quality=70)

            elif mime_type.startswith("video/"):
                result = subprocess.run([
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    str(config.STORAGE_DIR / file_id)
                ], capture_output=True, text=True)

                duration = float(json.loads(result.stdout)["format"]["duration"])
                timestamp = duration / 2

                cmd = [
                    "ffmpeg",
                    "-ss", str(timestamp),
                    "-i", str(config.STORAGE_DIR / file_id),
                    "-vframes", "1",
                    "-vf", "scale=300:-1",
                    str(config.STORAGE_DIR / f"{file_id}.jpg")
                ]
                try:
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    os.rename(config.STORAGE_DIR / f"{file_id}.jpg", config.STORAGE_DIR / f"{file_id}.preview")
                    preview_exists = True
                except FileNotFoundError:
                    pass

            elif mime_type == "application/x-msdownload":
                try:
                    extractor = IconExtractor(config.STORAGE_DIR / file_id)
                    extractor.export_icon(config.STORAGE_DIR / f"{file_id}.preview")
                    preview_exists = True
                except IconExtractorError:
                    pass

            split_filename = file.filename.split(".")
            filename = f"{split_filename[0][0:50 - (len(split_filename[-1]) + 1)]}.{split_filename[-1]}"

            await crud.insert_file(
                id=file_id,
                filename=filename,
                mime_type=mime_type,
                type=file.filename.split(".")[-1],
                size=file.size,
                preview=preview_exists,
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


@router.get("/files/{file_id}/preview")
async def get_preview(file_id: str):
    try:
        file = await crud.select_file(file_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The file doesn't exist"
        )

    file_type = file["type"]

    return FileResponse(config.STORAGE_DIR / f"{file_id}.preview", media_type=file_type)


@router.get("/files/{file_id}/meta")
async def get_file_metadata(file_id: str):
    return await crud.select_file(file_id)


@router.patch("/files/{file_id}")
async def update_file(file_id: str, schema: FileSchema):
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
    preview_path = config.STORAGE_DIR / f"{file_id}.preview"
    if preview_path.exists():
        os.remove(preview_path)

    await crud.delete_file(file_id)
