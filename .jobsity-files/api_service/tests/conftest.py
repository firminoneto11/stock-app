# encoding: utf-8

import pytest
from dotenv import load_dotenv

from api_service.models import User
from api_service.app import create_app
from api_service.extensions import db as _db
from pytest_factoryboy import register
from .factories import UserFactory


register(UserFactory)


@pytest.fixture(scope="session")
def app():
    load_dotenv(".testenv")
    app = create_app(testing=True)
    return app


@pytest.fixture
def db(app):
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture
def admin_user(db):
    user = User(
        username='admin',
        email='admin@admin.com',
        password='admin',
        role='ADMIN'
    )

    db.session.add(user)
    db.session.commit()

    return user
