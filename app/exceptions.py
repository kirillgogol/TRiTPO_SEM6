class ExistingEmailError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class NonExistentEmailError(Exception):
    pass


class IncorrectPasswordError(Exception):
    pass


class UnothorizedAccessError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class ArticleNotFoundError(Exception):
    pass


class FileUrlError(Exception):
    pass


class AccessTokenExpiredError(Exception):
    pass


class RefreshTokenExpiredError(Exception):
    pass

class TwilioError(Exception):
    pass