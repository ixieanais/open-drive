from fastapi import Request

from database import crud

from .service import Service


class HomeService(Service):
    def __init__(self, request: Request):
        self.request = request

    async def get_context(self):
        path = "/home"
        folder_id = await crud.select_folder_id(path)
        return {
            "current_folder": await crud.select_folder(folder_id),
            "folders": await crud.select_folders(folder_id),
            "files": await crud.select_files(folder_id),
            "disk_usage": await self.get_disk_usage(),
            "favorites": await crud.select_favorites(),
        }
