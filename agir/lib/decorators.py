from functools import wraps


def dont_vary_on_cookie(func):
    """
    Used with NoVaryCookieMiddleWare
    :param func:
    :return:
    """

    @wraps(func)
    def inner_func(*args, **kwargs):
        response = func(*args, **kwargs)
        response.dont_vary_on_cookie = True
        return response

    return inner_func
