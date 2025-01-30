from flask import request
from flask_restful import Resource
from api_service.api.schemas import StockInfoSchema
from api_service.extensions import db


class StockQuery(Resource):
    """
    Endpoint to allow users to query stocks
    """
    def get(self):
        # TODO: Call the stock service, save the response, and return the response to the user in
        # the format dictated by the StockInfoSchema.
        data_from_service = None
        schema = StockInfoSchema()
        return schema.dump(data_from_service)


class History(Resource):
    """
    Returns queries made by current user.
    """
    def get(self):
        # TODO: Implement this method.
        pass


class Stats(Resource):
    """
    Allows admin users to see which are the most queried stocks.
    """
    def get(self):
        # TODO: Implement this method.
        pass
