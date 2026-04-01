from contextlib import asynccontextmanager
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

import config
from api import router as api_router
from database import crud
from services import FolderService, HomeService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await crud.create_tables()
    try:
        id = str(uuid4())
        await crud.insert_folder(id, "/home")
    except IntegrityError:
        pass

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
tempaltes = Jinja2Templates(directory=config.TEMPLATES_DIR)


@app.get("/", tags=["pages"])
async def root_page():
    return RedirectResponse("/home")


@app.get("/home", tags=["pages"])
async def home_page(request: Request):
    service = HomeService()
    return tempaltes.TemplateResponse(
        request=request, name="index.html", context=await service.get_context()
    )


# @app.get("/starred")
# async def starred_page():
#     pass


# @app.get("/recent", tags=["pages"])
# async def recent_page(request: Request):
#     service = RecentService()
#     return tempaltes.TemplateResponse(
#         request=request,
#         name="index.html",
#         context=await service.get_context()
#     )


# @app.get("/graph")
# async def graph_page():
#     pass


# @app.get("/trash")
# async def trash_page():
#     pass


@app.get("/folders/{folder_id}", tags=["pages"])
async def folder_page(request: Request, folder_id: str):
    if not await crud.is_folder_exists(folder_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if await crud.is_main_folder(folder_id):
        return RedirectResponse("/home")

    service = FolderService(folder_id)
    return tempaltes.TemplateResponse(
        request=request, name="index.html", context=await service.get_context()
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
