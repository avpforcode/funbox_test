import abc
import time
from db import DBEngine
from importlib import import_module
from redis.exceptions import DataError


def get_model(model_name: str, db_engine: DBEngine):
    """ Function imports appropriate class to handle database request

    :param model_name:
    :param db_engine:
    :return:
    """
    class_name = "{}{}Model".format(model_name.title(), db_engine.name.title())
    module = import_module('models')

    try:
        return getattr(module, class_name)(db_engine)
    except AttributeError:
        raise ImportError(f'Module "models" doesnt have a {class_name} class')


class DomainModel(abc.ABC):
    """ Domain model interface. """
    db_engine = None

    @abc.abstractmethod
    def select_domains(self, *args, **kwargs):
        """ Get domains list from database.

        :param args:
        :param kwargs:
        :return:
        """

    @abc.abstractmethod
    def insert_domains(self, *args, **kwargs):
        """ Save domains list from database.

        :param args:
        :param kwargs:
        :return:
        """


class ModelError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return self.message


def select_output_handler(method):
    """ Correct format of domains names returning from database. """
    def wrapper(self, _from, to, *args, **kwargs):
        domains = set()
        data = method(self, _from, to,  *args, **kwargs)

        for domain in data:
            domain = domain[0].decode('utf-8')
            domain = domain.split(":")
            domains.add(domain[0])

        return domains

    return wrapper


class DomainsRedisModel(DomainModel):
    def __init__(self, db_engine: DBEngine):
        self.db_engine = db_engine

    @select_output_handler
    def select_domains(self, _from: int = None, to: int = None):
        if _from is None:
            _from = "-inf"
        if to is None:
            to = "+inf"

        try:
            with self.db_engine as cursor:
                return cursor.zrangebyscore("links", _from, to, withscores = True)
        except DataError as e:
            raise ModelError("Invalid redis request") from e

    def insert_domains(self, domains: list):
        try:
            with self.db_engine as cursor:
                for domain in domains:
                    cursor.zadd('links', {f"{domain}:{time.time()}": int(time.time())})
        except DataError as e:
            raise ModelError("Invalid redis request") from e
