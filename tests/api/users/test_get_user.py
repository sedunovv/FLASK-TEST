import json
from base64 import b64encode
from hamcrest import *  # noqa


def test_get_user(test_client):
    credentials = b64encode(b"test2@gmail.com:test2").decode('utf-8')
    response = test_client.post('/api/tokens', headers={"Authorization": f"Basic {credentials}"})
    assert_that(response.status_code, equal_to(200))

    data = json.loads(response.data)
    response = test_client.get('api/users/2', headers={"Authorization": f"Bearer {data['token']}"})
    assert_that(response.status_code, equal_to(200))

    user = json.loads(response.data)
    assert_that(user['id'], equal_to(2))
    assert_that(user['username'], equal_to('test2'))
    assert_that(user['email'], equal_to('test2@gmail.com'))
    assert_that(user['currency']['quote'], equal_to('AED'))


def test_get_user_403(test_client):
    credentials = b64encode(b"test2@gmail.com:test2").decode('utf-8')
    response = test_client.post('/api/tokens', headers={"Authorization": f"Basic {credentials}"})
    assert_that(response.status_code, equal_to(200))

    data = json.loads(response.data)
    response = test_client.get('api/users/1', headers={"Authorization": f"Bearer {data['token']}"})
    assert_that(response.status_code, equal_to(403))
