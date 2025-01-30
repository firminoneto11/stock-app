#!/bin/bash

alembic upgrade head;

python3 manage.py createuser user user;
python3 manage.py createuser superuser superuser --is-superuser;

python3 manage.py login user user;
python3 manage.py login superuser superuser;

python3 manage.py runserver;
