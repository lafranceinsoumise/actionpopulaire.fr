from rest_framework.views import exception_handler as original_exception_handler
from rest_framework.exceptions import ValidationError


def exception_handler(exc, context):
    """Custom exception handler

    Returns status code 422 specifically for validation errors

    :param exc:
    :param context:
    :return:
    """
    res = original_exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        res.status_code = 422

    return res
