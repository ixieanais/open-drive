import json
import shutil

from config import STORAGE_DIR
from database import crud


class Service:
    async def get_disk_usage(self):
        total, used, free = shutil.disk_usage(STORAGE_DIR)
        cloud_used = int(await crud.select_files_size())
        return json.dumps({"total": total - (used - cloud_used), "used": cloud_used})
