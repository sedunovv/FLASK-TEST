import json
from base64 import b64encode
from hamcrest import *  # noqa


def test_login_logout(test_client):
    credentials = b64encode(b"test2@gmail.com:test2").decode('utf-8')
    response = test_client.post('/api/tokens', headers={"Authorization": f"Basic {credentials}"})
    assert_that(response.status_code, equal_to(200))

    data = json.loads(response.data)
    response = test_client.delete('/api/tokens', headers={"Authorization": f"Bearer {data['token']}"})
    assert_that(response.status_code, equal_to(204))
