import smtplib
import socket

import requests
from celery import shared_task
from functools import wraps

from django.core.exceptions import ObjectDoesNotExist


def retry_strategy(
    start=None,
    increment=0,
    retry_on=(Exception,),
    max=3600 * 12,
    min=0,
    exp_base=2,
    forward_self=False,
):
    def outer(decorated):
        @wraps(decorated)
        def inner(self, *args, **kwargs):
            if forward_self:
                args = [self, *args]
            try:
                decorated(*args, **kwargs)
            except retry_on as e:
                import builtins

                if increment:
                    countdown = start + increment * self.request.retries
                else:
                    countdown = (
                        start * exp_base**self.request.retries
                    )  # self.retries starts at 0

                countdown = builtins.max(builtins.min(countdown, max), min)
                self.retry(countdown=countdown, exc=e)

        return inner

    return outer


def retriable_task(
    *args,
    bind=False,
    start=None,
    increment=0,
    retry_on=(Exception,),
    max=3600 * 12,
    min=0,
    exp_base=2,
    strategy=None,
    **kwargs,
):
    if strategy is None:
        strategy = retry_strategy(
            forward_self=bind,
            start=start,
            increment=increment,
            retry_on=retry_on,
            max=max,
            min=min,
            exp_base=exp_base,
        )

    taskifier = shared_task(bind=True, **kwargs)

    def decorate(f):
        return taskifier(strategy(f))

    if len(args) == 1:
        return decorate(args[0])
    return decorate


retry_on_http_strategy = retry_strategy(
    start=10, retry_on=(requests.RequestException, requests.exceptions.Timeout)
)
retry_on_http_and_object_does_not_exist_strategy = retry_strategy(
    start=10,
    retry_on=(
        requests.RequestException,
        requests.exceptions.Timeout,
        ObjectDoesNotExist,
    ),
)
retry_on_smtp_strategy = retry_strategy(
    start=10, retry_on=(smtplib.SMTPException, socket.error)
)
retry_on_smtp_and_object_does_not_exist_strategy = retry_strategy(
    start=10,
    retry_on=(
        smtplib.SMTPException,
        socket.error,
        ObjectDoesNotExist,
    ),
)
retry_on_object_does_not_exist_strategy = retry_strategy(
    start=10, retry_on=(ObjectDoesNotExist,)
)

http_task = retriable_task(strategy=retry_on_http_strategy)
post_save_http_task = retriable_task(
    strategy=retry_on_http_and_object_does_not_exist_strategy
)
emailing_task = retriable_task(strategy=retry_on_smtp_strategy)
post_save_emailing_task = retriable_task(
    strategy=retry_on_smtp_and_object_does_not_exist_strategy
)
post_save_task = retriable_task(strategy=retry_on_object_does_not_exist_strategy)
