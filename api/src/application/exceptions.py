class BaseException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class JWTError(BaseException): ...


class ServiceException(BaseException): ...
