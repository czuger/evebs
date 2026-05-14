import time


class EsiError(Exception):
    def should_retry(self):
        return False

    def pause(self):
        pass


class GatewayTimeout(EsiError):
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(10)


class BadGateway(EsiError):
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(5)


class ServiceUnavailable(EsiError):
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(30)


class ErrorLimited(EsiError):
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(60)


class OpenTimeout(EsiError):
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(5)


class SocketError(EsiError):
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(5)


class Forbidden(EsiError):
    pass


class NotFound(EsiError):
    pass


class UnknownError(EsiError):
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(30)


def dispatch(status_code, message=''):
    mapping = {
        500: GatewayTimeout,
        504: GatewayTimeout,
        502: BadGateway,
        403: Forbidden,
        420: ErrorLimited,
        404: NotFound,
        503: ServiceUnavailable,
        520: UnknownError,
    }
    cls = mapping.get(status_code)
    if cls:
        return cls(f'HTTP {status_code}: {message}')
    raise RuntimeError(f'Unhandled ESI error {status_code}: {message}')
