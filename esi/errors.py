import time


class EsiError(Exception):
    """Base class for all ESI response errors."""

    def should_retry(self):
        return False

    def pause(self):
        pass


class GatewayTimeout(EsiError):
    """HTTP 500/504: gateway timeout; retried after 10s."""

    def should_retry(self):
        return True

    def pause(self):
        time.sleep(10)


class BadGateway(EsiError):
    """HTTP 502: bad gateway; retried after 5s."""

    def should_retry(self):
        return True

    def pause(self):
        time.sleep(5)


class ServiceUnavailable(EsiError):
    """HTTP 503: service unavailable; retried after 30s."""

    def should_retry(self):
        return True

    def pause(self):
        time.sleep(30)


class ErrorLimited(EsiError):
    """Legacy 420: more than 100 non-2xx/3xx responses per minute."""
    def should_retry(self):
        return True

    def pause(self):
        time.sleep(60)


class RateLimited(EsiError):
    """HTTP 429: token-bucket rate limit; waits for the Retry-After interval."""
    def __init__(self, message='', retry_after=60):
        super().__init__(message)
        self._retry_after = int(retry_after)

    def should_retry(self):
        return True

    def pause(self):
        time.sleep(self._retry_after)


class OpenTimeout(EsiError):
    """Network-level request timeout; retried after 5s."""

    def should_retry(self):
        return True

    def pause(self):
        time.sleep(5)


class SocketError(EsiError):
    """Network-level connection error; retried after 5s."""

    def should_retry(self):
        return True

    def pause(self):
        time.sleep(5)


class Forbidden(EsiError):
    """HTTP 403: access denied; not retried."""


class NotFound(EsiError):
    """HTTP 404: resource not found; not retried."""


class UnknownError(EsiError):
    """HTTP 520: unknown/unhandled ESI error; retried after 30s."""

    def should_retry(self):
        return True

    def pause(self):
        time.sleep(30)


def dispatch(status_code, message=''):
    """Map an HTTP status code to the appropriate EsiError subclass."""
    mapping = {
        500: GatewayTimeout,
        504: GatewayTimeout,
        502: BadGateway,
        403: Forbidden,
        404: NotFound,
        420: ErrorLimited,
        429: RateLimited,
        503: ServiceUnavailable,
        520: UnknownError,
    }
    cls = mapping.get(status_code)
    if cls:
        return cls(f'HTTP {status_code}: {message}')
    raise RuntimeError(f'Unhandled ESI error {status_code}: {message}')
