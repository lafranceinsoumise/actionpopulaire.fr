from functools import wraps

from locust.contrib.fasthttp import FastHttpUser


class AgirHttpUser(FastHttpUser):
    abstract = True

    def __init__(self, environment):
        super().__init__(environment)
        self.headers = {}

        orig_request = self.client.request

        @wraps(orig_request)
        def request(*args, **kwargs):
            if len(args) >= 7:
                headers = args[6].copy()
                args = [*args[:6], headers, *args[7:]]
            else:
                headers = kwargs.setdefault("headers", {})

            for k, v in self.headers.items():
                headers.setdefault(k, v)

            return orig_request(*args, **kwargs)

        self.client.request = request
