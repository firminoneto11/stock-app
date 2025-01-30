from quart import jsonify

from src.application.exceptions import ServiceException


async def handle_service_exception(error: ServiceException):
    return jsonify({"detail": error.message}), error.code


def get_handlers():
    return {
        ServiceException: handle_service_exception,
    }
