from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from agir.voting_proxies.actions import (
    match_available_proxies_with_requests,
    find_voting_proxy_candidates_for_requests,
)


def fulfill_voting_proxy_requests(request, pk, pending_requests):
    matching_found = 0
    invitations_sent = 0

    if pending_requests.exists():
        # Find match with available proxies
        fulfilled_ids = match_available_proxies_with_requests(pending_requests)
        matching_found = len(fulfilled_ids)
        if matching_found > 0:
            pending_requests = pending_requests.exclude(id__in=fulfilled_ids)

        # Find voting proxy candidates
        if pending_requests.exists():
            _, candidate_ids = find_voting_proxy_candidates_for_requests(
                pending_requests
            )
            invitations_sent = len(candidate_ids)

    if matching_found + invitations_sent > 0:
        message = ""
        if matching_found == 0:
            message = f"Aucun volontaire disponible n'a été trouvé pour cette demande."
        elif matching_found == 1:
            message = f"Une demande a été satisfaite. Le volontaire a reçu une demande de confirmation."
        elif matching_found > 1:
            message = (
                f"{matching_found} demandes ont été satisfaites. "
                f"Les volontaires ont reçu une demande de confirmation."
            )

        if invitations_sent == 1:
            message += f" Une invitation a été envoyée."
        if invitations_sent > 1:
            message += f" {matching_found} invitations ont été envoyées."

        messages.add_message(request=request, level=messages.SUCCESS, message=message)
    else:
        messages.add_message(
            request=request,
            level=messages.WARNING,
            message="Aucun volontaire (disponible ou candidat) n'a été trouvé pour cette demande :-(",
        )

    return HttpResponseRedirect(
        reverse(
            "admin:voting_proxies_votingproxyrequest_change",
            args=(pk,),
        ),
    )
