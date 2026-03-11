from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..libs.adapters import (
    InMemoryAdapter,
    PostgresAdapter,
    RedisAdapter,
    SqliteAdapter,
    create_in_memory_adapter,
    create_postgres_adapter,
    create_redis_adapter,
    create_sqlite_adapter,
)


@dataclass(frozen=True)
class AdapterFactoryOptions:
    type: str = "inmemory"
    sqlite_path: Optional[str] = None
    postgres_dsn: Optional[str] = None
    redis_url: Optional[str] = None


class AdapterFactory:
    @staticmethod
    def create(options: AdapterFactoryOptions):
        adapter_type = options.type.lower()
        if adapter_type == "inmemory":
            return create_in_memory_adapter()
        if adapter_type == "sqlite":
            if not options.sqlite_path:
                raise ValueError("sqlite_path is required for sqlite adapter")
            return create_sqlite_adapter(options.sqlite_path)
        if adapter_type == "postgres":
            if not options.postgres_dsn:
                raise ValueError("postgres_dsn is required for postgres adapter")
            return create_postgres_adapter(options.postgres_dsn)
        if adapter_type == "redis":
            return create_redis_adapter(options.redis_url or "redis://localhost:6379")
        raise ValueError(f"Unsupported adapter type: {options.type}")


def createInMemoryAdapter() -> InMemoryAdapter:
    return create_in_memory_adapter()


def createSqliteAdapter(db_path: str) -> SqliteAdapter:
    return create_sqlite_adapter(db_path)


def createPostgresAdapter(dsn: str) -> PostgresAdapter:
    return create_postgres_adapter(dsn)


def createRedisAdapter(redis_url: str = "redis://localhost:6379") -> RedisAdapter:
    return create_redis_adapter(redis_url)
