import json
from base64 import b64encode
from hamcrest import *  # noqa


def test_make_transaction(test_client):
    credentials = b64encode(b"test1@gmail.com:test1").decode('utf-8')
    response = test_client.post('/api/tokens', headers={"Authorization": f"Basic {credentials}"})
    assert_that(response.status_code, equal_to(200))

    data = json.loads(response.data)
    response = test_client.get('api/users/1', headers={"Authorization": f"Bearer {data['token']}"})
    assert_that(response.status_code, equal_to(200))

    user = json.loads(response.data)
    assert_that(user['id'], equal_to(1))
    assert_that(user['username'], equal_to('test1'))
    assert_that(user['email'], equal_to('test1@gmail.com'))
    assert_that(user['currency']['quote'], equal_to('USD'))
    assert_that(user['bill'], equal_to(100.0))

    response = test_client.post('api/transactions', headers={"Authorization": f"Bearer {data['token']}",
                                                             "Content-Type": "application/json"},
                                data=json.dumps(dict(sender=1, recipient="test2@gmail.com", transfer_amount=10)))
    assert_that(response.status_code, equal_to(200))

    transaction = json.loads(response.data)
    assert_that(transaction['sender']['email'], equal_to('test1@gmail.com'))
    assert_that(transaction['recipient'], equal_to('test2@gmail.com'))

    response = test_client.get('api/users/1', headers={"Authorization": f"Bearer {data['token']}"})
    assert_that(response.status_code, equal_to(200))

    user = json.loads(response.data)
    assert_that(user['id'], equal_to(1))
    assert_that(user['username'], equal_to('test1'))
    assert_that(user['email'], equal_to('test1@gmail.com'))
    assert_that(user['currency']['quote'], equal_to('USD'))
    assert_that(user['bill'], equal_to(90.0))
