from uuid import UUID

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404, FileResponse
from django.shortcuts import reverse
from django.utils.translation import ngettext

from agir.event_requests import actions
from agir.event_requests.actions import (
    EventSpeakerRequestValidationError,
    EventRequestValidationError,
)
from agir.event_requests.models import EventRequest
from agir.events.models import Event


def accept_event_speaker_request(model_admin, request, pk):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    event_speaker_request = model_admin.get_object(request, pk)

    if event_speaker_request is None:
        raise Http404("La demande de disponibilité n'a pas pu être retrouvée.")

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

    try:
        actions.accept_event_speaker_request(event_speaker_request)
    except EventSpeakerRequestValidationError as e:
        messages.warning(request, str(e))
    else:
        if event_speaker_request.event_request.event:
            success_message = """
            La demande d'événement a été validée et un événement a été automatiquement créé. 
            Si des visuels sont en cours de génération, ils seront disponibles dans quelques 
            minutes sur la page d'administration de l'événement.
            """
        else:
            success_message = "L'intervenant·e sélectionné·e a bien été validé·e pour la date choisie."
        messages.success(request, success_message)

    return response


def unaccept_event_speaker_request(model_admin, request, pk):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    event_speaker_request = model_admin.get_object(request, pk)

    if event_speaker_request is None:
        raise Http404("La demande de disponibilité n'a pas pu être retrouvée.")

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

    try:
        actions.unaccept_event_speaker_request(event_speaker_request)
    except EventSpeakerRequestValidationError as e:
        messages.warning(request, str(e))
    else:
        messages.success(request, "La validation sélectionnée a bien été annulée.")

    return response


def accept_event_request(model_admin, request, pk):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    event_request = model_admin.get_object(request, pk)

    if event_request is None:
        raise Http404("La demande d'événement n'a pas pu être retrouvée.")

    response = HttpResponseRedirect(
        reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                EventRequest._meta.app_label,
                EventRequest._meta.model_name,
            ),
            args=(event_request.id,),
        )
    )

    try:
        actions.accept_event_request(event_request)
    except EventRequestValidationError as e:
        messages.warning(request, str(e))
    else:
        success_message = """
        La demande d'événement a été validée et un événement a été automatiquement créé. 
        Si des visuels sont en cours de génération, ils seront disponibles dans quelques 
        minutes sur la page d'administration de l'événement.
        """
        messages.success(request, success_message)

    return response


def set_event_asset_as_event_image(model_admin, request, pk):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    event_asset = model_admin.get_object(request, pk)

    if event_asset is None:
        raise Http404("Le visuel n'a pas pu être retrouvé.")

    response = HttpResponseRedirect(
        reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                Event._meta.app_label,
                Event._meta.model_name,
            ),
            args=(event_asset.event.id,),
        )
    )

    if event_asset.is_event_image_candidate:
        event_asset.set_as_event_image(event_asset.file)
        messages.success(request, "L'image de l'événement a bien été mise à jour")
    else:
        messages.warning(
            request, "Ce visuel ne peut pas être utilisé comme image d'événement"
        )

    return response


def preview_event_asset(model_admin, request, pk):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    event_asset = model_admin.get_object(request, pk)

    if event_asset is None:
        raise Http404("Le visuel n'a pas pu être retrouvé.")

    file = event_asset.render_preview()

    return FileResponse(file)


def render_event_asset(model_admin, request, event_asset):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    if not isinstance(event_asset, model_admin.model):
        event_asset = model_admin.get_object(request, event_asset)

        if event_asset is None:
            raise Http404("Le visuel n'a pas pu être retrouvé.")

        redirect_to = reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                Event._meta.app_label,
                Event._meta.model_name,
            ),
            args=(event_asset.event_id,),
        )
    else:
        redirect_to = reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                model_admin.model._meta.app_label,
                model_admin.model._meta.model_name,
            ),
            args=(event_asset.id,),
        )

    try:
        event_asset.render()
        model_admin.message_user(
            request, "Un nouveau visuel a été régénéré à partir du template."
        )
    except Exception as e:
        model_admin.message_user(
            request,
            str(e),
            level=messages.WARNING,
        )
    return HttpResponseRedirect(redirect_to + f"?{request.GET.urlencode()}")


def publish_event_assets(model_admin, request, target):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    queryset = target
    redirect_to = "."

    if isinstance(target, str) or isinstance(target, UUID):
        queryset = model_admin.model.objects.filter(pk=target)

        if not queryset.first():
            raise Http404("Le visuel n'a pas pu être retrouvé.")

        redirect_to = reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                Event._meta.app_label,
                Event._meta.model_name,
            ),
            args=(queryset.first().event_id,),
        )
    elif isinstance(target, model_admin.model):
        queryset = model_admin.model.objects.filter(pk=target.pk)
        redirect_to = reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                model_admin.model._meta.app_label,
                model_admin.model._meta.model_name,
            ),
            args=(target.pk,),
        )

    try:
        updated_count = actions.publish_event_assets(queryset)
        model_admin.message_user(
            request,
            ngettext(
                "Le visuel a été publié.",
                f"{updated_count} visuels ont été publiés",
                updated_count,
            ),
        )
    except Exception as e:
        model_admin.message_user(
            request,
            str(e),
            level=messages.WARNING,
        )
    return HttpResponseRedirect(redirect_to + f"?{request.GET.urlencode()}")


def unpublish_event_assets(model_admin, request, target):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    queryset = target
    redirect_to = "."

    if isinstance(target, str) or isinstance(target, UUID):
        queryset = model_admin.model.objects.filter(pk=target)

        if not queryset.first():
            raise Http404("Le visuel n'a pas pu être retrouvé.")

        redirect_to = reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                Event._meta.app_label,
                Event._meta.model_name,
            ),
            args=(queryset.first().event_id,),
        )
    elif isinstance(target, model_admin.model):
        queryset = model_admin.model.objects.filter(pk=target.pk)
        redirect_to = reverse(
            "%s:%s_%s_change"
            % (
                model_admin.admin_site.name,
                model_admin.model._meta.app_label,
                model_admin.model._meta.model_name,
            ),
            args=(target.pk,),
        )

    try:
        updated_count = actions.unpublish_event_assets(queryset)
        model_admin.message_user(
            request,
            ngettext(
                "Le visuel a été dépublié.",
                f"{updated_count} visuels ont été dépubliés",
                updated_count,
            ),
        )
    except Exception as e:
        model_admin.message_user(
            request,
            str(e),
            level=messages.WARNING,
        )

    return HttpResponseRedirect(redirect_to + f"?{request.GET.urlencode()}")
