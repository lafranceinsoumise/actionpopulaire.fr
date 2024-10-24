import smtplib
import socket
from functools import wraps

import requests
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from firebase_admin.exceptions import FirebaseError

TASK_PRIORITY_LOW = settings.CELERY_TASK_PRIORITY_LOW
TASK_PRIORITY_NORMAL = settings.CELERY_TASK_PRIORITY_NORMAL
TASK_PRIORITY_HIGH = settings.CELERY_TASK_PRIORITY_HIGH


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


def http_task(post_save=False, priority=TASK_PRIORITY_LOW):
    retry_on = (
        requests.RequestException,
        requests.exceptions.Timeout,
    )
    if post_save:
        retry_on = (*retry_on, ObjectDoesNotExist)

    return retriable_task(
        strategy=retry_strategy(start=10, retry_on=retry_on), priority=priority
    )


def emailing_task(post_save=False, priority=TASK_PRIORITY_NORMAL):
    retry_on = (
        smtplib.SMTPException,
        socket.error,
    )
    if post_save:
        retry_on = (*retry_on, ObjectDoesNotExist)

    return retriable_task(
        strategy=retry_strategy(start=10, retry_on=retry_on), priority=priority
    )


def gcm_push_task(post_save=False):
    retry_on = (
        FirebaseError,
        requests.HTTPError,
        requests.RequestException,
        requests.exceptions.Timeout,
    )
    if post_save:
        retry_on = (*retry_on, ObjectDoesNotExist)

    return retriable_task(strategy=retry_strategy(start=10, retry_on=retry_on))


def post_save_task():
    return retriable_task(
        strategy=retry_strategy(start=10, retry_on=(ObjectDoesNotExist,))
    )
