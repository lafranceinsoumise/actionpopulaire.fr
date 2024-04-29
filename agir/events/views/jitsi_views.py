from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from agir.events.models import JitsiMeeting


@csrf_exempt
@require_POST
def jitsi_reservation_view(request):
    try:
        meeting = JitsiMeeting.objects.get(room_name=request.POST.get("name"))
    except JitsiMeeting.DoesNotExist:
        return JsonResponse({"message": "Cette conférence n'existe pas."}, status=404)
    else:
        if meeting.event is not None and not meeting.event.is_current():
            return JsonResponse(
                {
                    "message": "L'événement n'est pas encore commencé ou est déjà terminé."
                },
                status=403,
            )

        meeting.start_time = timezone.now()
        meeting.save(update_fields=["start_time"])

        return JsonResponse(
            {
                "id": meeting.pk,
                "name": meeting.room_name,
                "start_time": (
                    meeting.event.start_time.isoformat(timespec="milliseconds")
                    if meeting.event is not None
                    else timezone.now()
                ),
                "duration": (
                    int(
                        (
                            meeting.event.end_time - meeting.event.start_time
                        ).total_seconds()
                    )
                    if meeting.event is not None
                    else 3600
                ),
            }
        )


@csrf_exempt
@require_http_methods(["DELETE"])
def jitsi_delete_conference_view(request, pk):
    try:
        meeting = JitsiMeeting.objects.get(pk=pk)
        meeting.end_time = timezone.now()
        meeting.save(update_fields=["end_time"])
        return JsonResponse({"message": "Conférence terminée."})
    except JitsiMeeting.DoesNotExist:
        return JsonResponse({"message": "Cette conférence n'existe pas."}, status=404)
