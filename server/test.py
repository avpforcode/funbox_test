import hug
import main
import time
from falcon import HTTP_400, HTTP_200
from datetime import datetime, timedelta

post_body = {
    "links": [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",
        "funbox.ru",
        "localhost:4000/django",
        "http://127.0.0.1:8080",
        "htt:/wrong_link",
        234123,
        {"wrong_input_data": 123},
        ["wrong_input_data"]
    ]
}


def tests_get():
    time.sleep(1)
    # get only domains inserted right a second ago with 'tests_post'
    response = hug.test.call('GET', main, "visited_domains", {
        "_from": (datetime.now() - timedelta(seconds = 2)).timestamp(),
        "to": time.time()
    })

    assert response.status == HTTP_200
    assert response.data is not None
    assert response.data["status"] == "OK"
    assert sorted(response.data["domains"]) == sorted(['127.0.0.1', 'ya.ru', 'funbox.ru',
                                                       'localhost', 'stackoverflow.com'])


def tests_post():
    response = hug.test.call('POST', main, "visited_links", body = post_body)
    assert response.status == HTTP_200
    assert response.data is not None
    assert "htt:/wrong_link" in response.data['status']
    assert "234123" in response.data['status']
    assert str({"wrong_input_data": 123}) in response.data['status']
    assert str(["wrong_input_data"]) in response.data['status']

    response = hug.test.call('POST', main, "visited_links", body = post_body["links"][8])
    assert response.status == HTTP_400


tests_post()
tests_get()
