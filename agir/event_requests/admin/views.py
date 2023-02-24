from functools import partial

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import reverse

from agir.event_requests.actions import (
    create_event_from_event_speaker_request,
    schedule_new_event_tasks,
)
from agir.event_requests.models import EventRequest


def validate_event_speaker_request(model_admin, request, pk):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    event_speaker_request = model_admin.get_object(request, pk)

    if event_speaker_request is None:
        raise Http404("La demande de disponibilité n'a pas pu être retrouvée")

    error_message = None
    response = HttpResponseRedirect(
        reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                EventRequest._meta.app_label,
                EventRequest._meta.model_name,
            ),
            args=(event_speaker_request.event_request_id,),
        )
    )

    if event_speaker_request.event_request.status != EventRequest.Status.PENDING:
        error_message = "Cette demande d'événement ne peut plus être validée."

    if not event_speaker_request.available:
        error_message = "L'intervenant·e choisi·e n'est pas disponible pour cette événement pour la date indiquée."

    if event_speaker_request.event_request.event is not None:
        error_message = "Un événement a déjà été créé pour cette demande. Veuillez le supprimer avant d'en créer un autre."

    if error_message:
        messages.warning(request, error_message)
        return response

    with transaction.atomic():
        # Create the event
        event = create_event_from_event_speaker_request(event_speaker_request)

        if event:
            # Mark the event speaker request as accepted
            event_speaker_request.event_request.event_speaker_requests.update(
                accepted=False
            )
            event_speaker_request.accepted = True
            event_speaker_request.save()
            # Change the event request event and status
            event_speaker_request.event_request.event = event
            event_speaker_request.event_request.status = EventRequest.Status.DONE
            event_speaker_request.event_request.save()

            transaction.on_commit(
                partial(schedule_new_event_tasks, event_speaker_request.event_request)
            )

            messages.success(
                request,
                f"La demande d'événement a été validée et un événement a été automatiquement créé.",
            )

        return response
