from agir.lib.rest_framework_permissions import GlobalOrObjectPermissions


class EventSpeakerAPIPermissions(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
        "PATCH": [],
        "PUT": [],
    }
    object_perms_map = {
        "GET": ["event_requests.view_event_speaker"],
        "PATCH": ["event_requests.change_event_speaker"],
        "PUT": ["event_requests.change_event_speaker"],
    }


class EventSpeakerRequestAPIPermissions(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
        "PATCH": [],
        "PUT": [],
    }
    object_perms_map = {
        "GET": ["event_requests.view_event_speaker_request"],
        "PATCH": ["event_requests.change_event_speaker_request"],
        "PUT": ["event_requests.change_event_speaker_request"],
    }
