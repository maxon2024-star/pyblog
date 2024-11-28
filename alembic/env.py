from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import sys
import os

# Добавьте директорию проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импорт моделей из основного файла
from main import SQLModel, engine  

# Это задает конфигурацию логирования из файла alembic.ini
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Метаданные для отслеживания изменений базы данных
target_metadata = SQLModel.metadata

# URL базы данных (используется для миграций)
config = context.config
config.set_main_option("sqlalchemy.url", "postgresql+asyncpg://postgres:05062012@localhost:5432/pyblog")


def run_migrations_offline():
    """Запуск миграций в оффлайн-режиме."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запуск миграций в онлайн-режиме."""
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_connection: context.configure(
                connection=sync_connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        await connection.run_sync(lambda sync_connection: context.run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
