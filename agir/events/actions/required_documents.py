import datetime
from datetime import timedelta

from django.utils import timezone


def get_project_document_deadline(project):
    return project.event.end_time + timedelta(days=15)


def get_project_required_document_types(project):
    return project.event.subtype.required_documents


def get_project_sent_document_types(project):
    return project.documents.values_list("type", flat=True)


def get_project_dismissed_document_types(project):
    dismissed_types = []
    if (
        project.details
        and project.details.get("documents")
        and project.details["documents"].get("absent")
    ):
        dismissed_types = project.details["documents"]["absent"]

    return dismissed_types


def get_project_missing_documents(project):
    required_types = get_project_required_document_types(project)
    if len(required_types) == 0:
        return []
    dismissed_types = get_project_dismissed_document_types(project)
    required_types = [t for t in required_types if t not in dismissed_types]
    if len(required_types) == 0:
        return []
    sent_types = get_project_sent_document_types(project)
    required_types = [t for t in required_types if t not in sent_types]

    return required_types


def get_project_missing_document_count(project):
    return len(get_project_missing_documents(project))


def get_is_blocking_project(project):
    # Avoid blocking event creations before November the 1st 2021
    if datetime.date.today() < datetime.date(2021, 11, 1):
        return False

    deadline = get_project_document_deadline(project)
    if timezone.now() < deadline:
        return False

    missing_document_count = get_project_missing_document_count(project)
    return missing_document_count > 0
