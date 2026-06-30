from typing import Optional, Union

from sqlalchemy import text

from database.models import Base, FavoritesOrm, FilesOrm, FoldersOrm

from .database import engine, session_factory


async def create_tables():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def insert_file(
    id: str,
    filename: str,
    mime_type: Optional[str],
    type: Optional[str],
    size: str,
    preview: bool,
    folder_id: str,
):
    async with session_factory() as session:
        file = FilesOrm(
            id=id,
            filename=filename,
            mime_type=mime_type,
            type=type,
            size=size,
            preview=preview,
            folder_id=folder_id,
        )
        session.add(file)
        await session.commit()


async def select_files(folder_id: str) -> Union[list[dict], list]:
    async with session_factory() as session:
        stmt = text("""
            SELECT * FROM files WHERE folder_id = :folder_id ORDER BY updated_at DESC
        """).bindparams(folder_id=folder_id)
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


async def select_similar_files(query: str) -> Union[list[dict], list]:
    async with session_factory() as session:
        stmt = text(
            "SELECT * FROM files WHERE LOWER(filename) ILIKE '%' || LOWER(:query) || '%' LIMIT 25"
        ).bindparams(query=query)
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


async def select_recent_files() -> Union[list[dict], list]:
    async with session_factory() as session:
        stmt = text("SELECT * FROM files ORDER BY updated_at DESC LIMIT 50")
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


async def select_files_size() -> int:
    async with session_factory() as session:
        stmt = text("SELECT SUM(size) FROM files")
        result = await session.execute(stmt)
        row = result.one()
        return row[0] if row[0] else 0


async def select_file(id: str) -> dict:
    async with session_factory() as session:
        stmt = text("SELECT * FROM files WHERE id = :id").bindparams(id=id)
        result = await session.execute(stmt)
        row = result.mappings().one()
        return dict(row) if row else {}


async def select_file_type(id: str) -> Optional[str]:
    async with session_factory() as session:
        stmt = text("SELECT type FROM files WHERE id = :id").bindparams(id=id)
        result = await session.execute(stmt)
        row = result.first()
        return row[0] if row[0] else None


async def update_filename(id: str, filename: str):
    async with session_factory() as session:
        stmt = text("UPDATE files SET filename = :filename WHERE id = :id").bindparams(
            id=id, filename=filename
        )
        await session.execute(stmt)
        await session.commit()


async def update_file_location(id: str, folder_id: str):
    async with session_factory() as session:
        stmt = text(
            "UPDATE files SET folder_id = :folder_id WHERE id = :id"
        ).bindparams(id=id, folder_id=folder_id)
        await session.execute(stmt)
        await session.commit()


async def delete_file(id: str):
    async with session_factory() as session:
        stmt = text("DELETE FROM files WHERE id = :id").bindparams(id=id)
        await session.execute(stmt)
        await session.commit()


async def delete_files(folder_id: str):
    async with session_factory() as session:
        stmt = text("DELETE FROM files WHERE folder_id = :folder_id").bindparams(
            folder_id=folder_id
        )
        await session.execute(stmt)
        await session.commit()


async def insert_folder(id: str, path: str, parent_id: Optional[str] = None):
    async with session_factory() as session:
        folder = FoldersOrm(id=id, path=path, parent_id=parent_id)
        session.add(folder)
        await session.commit()


async def select_folders(parent_id: str) -> list[dict]:
    async with session_factory() as session:
        stmt = text("SELECT * FROM folders WHERE parent_id = :parent_id").bindparams(
            parent_id=parent_id
        )
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


async def select_recent_folders() -> list[dict]:
    async with session_factory() as session:
        stmt = text("SELECT * FROM folders ORDER BY updated_at DESC LIMIT 20")
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


async def select_folder(id: str) -> Optional[dict]:
    async with session_factory() as session:
        stmt = text("SELECT * FROM folders WHERE id = :id").bindparams(id=id)
        result = await session.execute(stmt)
        row = result.mappings().one()
        return dict(row) if row else None


async def select_similar_folders(query: str) -> Union[list[dict], list]:
    async with session_factory() as session:
        stmt = text(
            "SELECT * FROM folders WHERE LOWER(path) ILIKE LOWER(:query) || '%' LIMIT 25"
        ).bindparams(query=query)
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


async def select_folder_id(path: str) -> str:
    async with session_factory() as session:
        stmt = text("SELECT id FROM folders WHERE path = :path").bindparams(path=path)
        result = await session.execute(stmt)
        row = result.one()
        return row[0]


async def is_folder_exists(id: str) -> bool:
    async with session_factory() as session:
        stmt = text("SELECT 1 FROM folders WHERE id = :id").bindparams(id=id)
        result = await session.execute(stmt)
        row = result.first()
        return True if row else False


async def is_main_folder(id: str) -> bool:
    async with session_factory() as session:
        stmt = text("SELECT 1 FROM folders WHERE id = :id AND path = :path").bindparams(
            id=id, path="/home"
        )
        result = await session.execute(stmt)
        row = result.first()
        return True if row else False


async def update_folder(id: str, path: str):
    async with session_factory() as session:
        old_folder = await session.execute(
            text("SELECT path FROM folders WHERE id = :id").bindparams(id=id)
        )
        old_path = old_folder.scalar_one()

        await session.execute(
            text("UPDATE folders SET path = :path WHERE id = :id").bindparams(
                id=id, path=path
            )
        )

        await session.execute(
            text("""
                UPDATE folders
                SET path = :new_path || substr(path, :old_len + 1)
                WHERE path LIKE :like_pattern
            """).bindparams(
                new_path=path,
                old_len=len(old_path),
                like_pattern=f"{old_path}/%",
            )
        )
        await session.commit()


async def delete_folder(id: str):
    async with session_factory() as session:
        stmt = text("DELETE FROM folders WHERE id = :id").bindparams(id=id)
        await session.execute(stmt)
        await session.commit()


async def insert_favorite(folder_id: str):
    async with session_factory() as session:
        favorite = FavoritesOrm(folder_id=folder_id)
        session.add(favorite)
        await session.commit()


async def select_favorites() -> Union[list[dict], list]:
    async with session_factory() as session:
        stmt = text("""
            SELECT folders.*
            FROM folders
            INNER JOIN favorites ON folders.id = favorites.folder_id
            ORDER BY favorites.created_at ASC
        """)
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


async def delete_favorite(folder_id: str):
    async with session_factory() as session:
        stmt = text("DELETE FROM favorites WHERE folder_id = :folder_id").bindparams(
            folder_id=folder_id
        )
        await session.execute(stmt)
        await session.commit()
