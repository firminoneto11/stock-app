# encoding: utf-8

from flask_httpauth import HTTPBasicAuth

from api_service.models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify(username, password):
    # TODO: Use the data in the database to validate the user credentials.
    return False
