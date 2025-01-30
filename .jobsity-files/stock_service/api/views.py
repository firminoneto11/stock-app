# encoding: utf-8

from flask import Blueprint, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from stock_service.api.resources import StockResource


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)


api.add_resource(StockResource, "/stock", endpoint="stock")


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    return jsonify(e.messages), 400
