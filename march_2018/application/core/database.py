from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import (
    database_exists,
    create_database,
    drop_database
)

from core.utils import import_settings
from core.exceptions import DatabaseError


BaseModel = declarative_base()


def get_config(name=None):
    """
    Вернуть словарь из settings.DATABASES по ключу.
    Словарь можно использовать для подключения к базе данных.
    Если name не задан, то вернуть дефолтовый конфиг
    для подключения без указания базы данных.
    """
    settings = import_settings()
    if name:
        config = settings.DATABASES[name]
    else:
        config = settings.DATABASES['default']
        config['name'] = ''

    return config


def get_engine(config=None, echo=False, echo_pool=False):
    """
    Вернуть engine базы данных по заданному конфигу.
    Если config не задан, то вернуть engine без указания базы данных.
    echo и echo_pool использовать при дебаге.
    """
    if not config:
        config = get_config()
    template = '{provider}://{username}:{password}@{host}/{name}'
    engine = create_engine(
        template.format(**config),
        echo=echo,
        echo_pool=echo_pool
    )
    return engine


def get_sessionmaker(name=None):
    """
    Вернуть sessionmaker указанной базы данных.
    По умолчанию вернуть sessionmaker без базы данных.
    """
    config = get_config(name)
    engine = get_engine(config)
    return sessionmaker(bind=engine)


@contextmanager
def transaction(sessionmaker):
    """Выполнить транзакцию. Использовать с with."""
    session = sessionmaker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class Database:
    def __init__(self, name=None, echo=False, echo_pool=False):
        self.config = get_config(name)
        self.engine = get_engine(self.config, echo, echo_pool)
        self.sessionmaker = get_sessionmaker(name)

    @property
    def is_present(self):
        return database_exists(self.engine.url)

    def create(self):
        if not self.is_present:
            create_database(self.engine.url)
        else:
            raise DatabaseError('Database already exists')

    def drop(self):
        if self.is_present:
            drop_database(self.engine.url)
        else:
            raise DatabaseError("Database doesn't exist")

    def create_tables(self):
        BaseModel.metadata.create_all(self.engine)

    def drop_tables(self):
        BaseModel.metadata.drop_all(self.engine)
