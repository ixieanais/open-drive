from fastapi import Request

from database import crud

from .service import Service


class FolderService(Service):
    def __init__(self, request: Request, folder_id):
        self.request = request
        self.folder_id = folder_id

    async def get_context(self):
        curr_folder = await crud.select_folder(self.folder_id)
        return {
            "current_folder": curr_folder,
            "parent_folder_is_main": await crud.is_main_folder(
                curr_folder.get("parent_id")
            ),
            "folders": await crud.select_folders(self.folder_id),
            "files": await crud.select_files(self.folder_id),
            "disk_usage": await self.get_disk_usage(),
            "favorites": await crud.select_favorites(),
        }
