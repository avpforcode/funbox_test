import os
import redis

REDIS_DB = "redis"


class InitDB:
    """ Read base server config and choose database engine
    Call instance of that class to get db_engine instance

    Usage:
    db_inst = InitDB()
    db_engine = db_inst()
    """
    supported_databases = [REDIS_DB]  # there is could be not only redis

    def __init__(self):
        self.engine = os.environ.get("DATABASE_ENGINE", None)
        self.address = os.environ.get("DATABASE_HOST", None)
        self.port = int(os.environ.get("DATABASE_PORT", None))

        if (not self.engine or not self.address
                or self.engine not in self.supported_databases):
            raise EnvironmentError("Invalid database configuration, "
                                   "please check your environments")

    def __call__(self, *args, **kwargs):
        if self.engine == REDIS_DB:
            port = self.port if self.port else 6379
            return RedisEngine(self.address, port)
        else:
            raise EnvironmentError("Invalid database configuration, "
                                   "please check your environments")


class DBEngine:
    """ Base database engine class. It needs for typing """
    name = None


class RedisEngine(DBEngine):
    """ Return redis-py connection object.
    Use redis with context manager.
    """
    def __init__(self, address: str, port: int = 6379, database_number: int = 0):
        self.name = REDIS_DB
        self.address = address
        self.port = port
        self.db = database_number
        self.client = None

    def __enter__(self):
        self.connect()
        return self.client

    def __exit__(self, *args, **kwargs):
        """ Do nothing at the output """

    def connect(self):
        if not self.client:
            self.client = redis.Redis(host = self.address, port = self.port, db = self.db)
