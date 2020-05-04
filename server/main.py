import hug
from db import InitDB
from utils import init_log
from falcon.request import Request
from falcon.response import Response
from models import ModelError, get_model
from serializers import LinksSerializer, TimeSerializer

""" Инстанс базы данных инициализируется исходя из настроек сервера. 
Инстанс лога должен сосдаваться один раз, поэтому глобальный """

db_engine = InitDB()
error_log = init_log("error")


@hug.request_middleware()
def process_data(request: Request, response: Response):
    """ 'from' is a build-in python name so we have to rename it before using.

    """
    if "from" in request.params:
        request.params["_from"] = request.params.pop("from")


@hug.get('/visited_domains')
def visited_domains(_from: TimeSerializer()=None, to: TimeSerializer()=None) -> dict:
    """ Visited_domains GET request controller

    :param _from: start of period
    :param to: end of period
    :return: list of visited domains during period
    """

    """ Проверять переменные _from и to лучше внутри сериализатора и там уже 
    поднимать исключение если что то не так, исключение вернет респонз со 
    статусом 400, но так как в задании указано что ошибки должны возвращаться
    в поле status ответа, в сериализаторе плохое значение я просто вкладываю 
    в словарь типа {"bad_value": value} и обрабатываю это уже в здесь в контроллере """

    if isinstance(_from, dict):
        return dict(domains=[], status="Bad start time")
    if isinstance(to, dict):
        return dict(domains=[], status="Bad end time")

    try:

        """ Модель данных в базе данных. Основная его цель - обращатся к базе 
        через единый интерфейс не задумываясь, какая база внизу. Для этого можно
        создавать классы тиа DomainsRedisModel или DomainsPostgresModel. 
        Функция get_model вернет нужный экземпляр такого класса в зависимости 
        от имени модели и настроек сервера."""

        db_model = get_model('domains', db_engine())
    except ImportError as e:
        error_log.error(e)
        return dict(status="Inner Server Error")

    try:
        domains = db_model.select_domains(_from, to)
    except ModelError as e:
        return dict(domains=[], status=e.message)
    else:
        return dict(domains=domains, status="OK")


@hug.post("/visited_links")
def visited_links(body: LinksSerializer()) -> dict:
    """ Visited_links POST request controller

    :body: dict of the type {links: [list of some URLs]}
           see LinksSerializer for details
    :return: status of request
    """
    try:
        db_model = get_model('domains', db_engine())
    except ImportError as e:
        error_log.error(e)
        return dict(status="Inner Server Error")

    try:

        """ Данная проверка делается по той же причине что и с переменными 
        _from,to из visited_domains"""

        good_links = [link for link in body["links"] if isinstance(link, str)]
        bad_links = "; ".join([link["bad_value"] for link in body["links"] if isinstance(link, dict)])

        if len(good_links):
            db_model.insert_domains(good_links)

        if bad_links:
            return dict(status = f"Next links is invalid: {bad_links}")

    except ModelError as e:
        error_log.error(e)
        return dict(status=e.message)
    else:
        return dict(status="OK")
