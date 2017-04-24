import rules


@rules.predicate
def is_organizer(user, event=None):
    return (
        event is not None and
        user.is_authenticated and
        user.organized_events.filter(pk=event.pk).exists()
    )


rules.add_perm('events.change_event', is_organizer)
