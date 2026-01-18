from __future__ import annotations
from typing import Protocol, Any
import asyncpg


class CollectionProtocol(Protocol):
    async def find(self, _filter) -> list[dict]: ...
    async def insert(self, _object) -> None: ...
    async def update(self, _filter, _object) -> None: ...
    async def delete(self, _filter) -> None: ...
    async def pop(self, _filter) -> dict: ...


class ConnectionProtocol(Protocol):
    async def __aenter__(self) -> ConnectionProtocol: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def __getattr__(self, key) -> CollectionProtocol: ...
    def commit(self) -> None: ...
    def collections(self) -> tuple[CollectionProtocol]: ...

class PostgresCollection(CollectionProtocol):
    async def find(self, _filter) -> list[dict]: ...
    async def insert(self, _object) -> None: ...
    async def update(self, _filter, _object) -> None: ...
    async def delete(self, _filter) -> None: ...
    async def pop(self, _filter) -> dict: ...

class PostgresConnection(ConnectionProtocol):
    def __init__(self, pool, autocommit=True):
        self.pool = pool
        self.connection
        self.transaction
        self.autocommit = autocommit
    
    async def __aenter__(self):
        self.connection = await self.pool.acquire()
        self.transaction = self.connection.transaction()
        await self.transaction.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.autocommit:
            await self.commit()
        await self.pool.release(self.connection)
        del self.__dict__['connection']
        del self.__dict__['transaction']
    
    async def __getattr__(self, key) -> CollectionProtocol:
        
    
    async def commit(self) -> None:
        await self.transaction.commit()
    
    async def collections(self) -> list:
        return [collection[0] for collection in await self._fetch('''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema') AND table_type = 'BASE TABLE'
            ORDER BY table_name;''')]
    
    async def _fetch(self, query, *args, timeout: float | None = None, record_class=None) -> list:
        return await self.connection.fetch(
            query,
            *args,
            timeout=timeout,
            record_class=None
        )


async def Postgres(
        dsn: Any | None = None,
        *,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
        server_settings: dict | None = None):
    return PostgresConnection(
        pool=await asyncpg.create_pool(
            dsn,
            host=host,
            user=user,
            password=password,
            database=database,
            server_settings=server_settings
        )
    )
