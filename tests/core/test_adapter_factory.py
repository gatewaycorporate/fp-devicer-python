import pytest

from devicer.core.adapter_factory import AdapterFactory, AdapterFactoryOptions


def test_inmemory_factory_returns_adapter():
    adapter = AdapterFactory.create(AdapterFactoryOptions(type="inmemory"))
    assert hasattr(adapter, "init")
    assert hasattr(adapter, "save")


@pytest.mark.asyncio
async def test_inmemory_init_resolves():
    adapter = AdapterFactory.create(AdapterFactoryOptions(type="inmemory"))
    await adapter.init()


def test_sqlite_missing_path_throws():
    with pytest.raises(ValueError, match="sqlite_path"):
        AdapterFactory.create(AdapterFactoryOptions(type="sqlite"))


def test_sqlite_with_path_returns_adapter(tmp_path):
    adapter = AdapterFactory.create(AdapterFactoryOptions(type="sqlite", sqlite_path=str(tmp_path / "db.sqlite")))
    assert hasattr(adapter, "init")


def test_postgres_missing_dsn_throws():
    with pytest.raises(ValueError, match="postgres_dsn"):
        AdapterFactory.create(AdapterFactoryOptions(type="postgres"))


def test_postgres_with_dsn_returns_adapter():
    adapter = AdapterFactory.create(AdapterFactoryOptions(type="postgres", postgres_dsn="postgresql://u:p@localhost/db"))
    assert hasattr(adapter, "init")


def test_redis_with_url_returns_adapter():
    adapter = AdapterFactory.create(AdapterFactoryOptions(type="redis", redis_url="redis://localhost:6379"))
    assert hasattr(adapter, "init")


def test_unknown_type_throws_with_type_name():
    with pytest.raises(ValueError, match="foobar"):
        AdapterFactory.create(AdapterFactoryOptions(type="foobar"))
