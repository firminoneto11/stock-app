# encoding: utf-8

from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from api_service.api import resources


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)


api.add_resource(resources.StockQuery, "/stock", endpoint="stock")
api.add_resource(resources.History, "/users/history", endpoint="users-history")
api.add_resource(resources.Stats, "/stats", endpoint="stats")


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    return jsonify(e.messages), 400
