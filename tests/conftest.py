import pytest
import os

from app import create_app
from app.models import *
from config import TestingConfig


@pytest.fixture(scope='module')
def test_client():
    app = create_app(TestingConfig)

    testing_client = app.test_client()

    with app.app_context():
        db.create_all()

        curr1 = Currency(base='EUR', quote='USD', rate=1.18425)
        curr2 = Currency(base='EUR', quote='AED', rate=4.32489)
        db.session.add(curr1)
        db.session.add(curr2)
        db.session.commit()
        data1 = {'username': 'test1', 'email': 'test1@gmail.com', 'password': 'test1', 'currency': 'USD', 'bill': 100}
        user1 = User()
        user1.from_dict(data1, new_user=True)
        db.session.add(user1)
        data2 = {'username': 'test2', 'email': 'test2@gmail.com', 'password': 'test2', 'currency': 'AED', 'bill': 100}
        user2 = User()
        user2.from_dict(data2, new_user=True)
        db.session.add(user2)

        yield testing_client

        db.session.remove()
        db.drop_all()
