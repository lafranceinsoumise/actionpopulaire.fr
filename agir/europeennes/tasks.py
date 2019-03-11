from celery import shared_task


@shared_task
def send_loan_email(person_id):
    pass
