from django.db import transaction


__all__ = ["merge_persons"]


def merge_attr_or(e1, e2, attr):
    setattr(e1, attr, getattr(e1, attr) or getattr(e2, attr))


def merge_persons(p1, p2):
    """Merge the two persons together, keeping p1 and deleting p2, associating all information linked to p2 to p1"""

    with transaction.atomic():
        # check if it's not the same user
        if p1.pk == p2.pk:
            raise ValueError

        # for memberships, we want to carefully copy the properties in case there is a duplicate
        current_memberships = p1.memberships.select_for_update()
        groups = {m.supportgroup_id: m for m in current_memberships}

        # copying person tags
        missing_tags = p2.tags.all().difference(p1.tags.all())
        p1.tags.add(*missing_tags)

        for m2 in p2.memberships.all():
            if m2.supportgroup_id in groups:
                m1 = groups[m2.supportgroup_id]
                m1.created = min(m1.created, m2.created)
                merge_attr_or(m1, m2, "is_referent")
                merge_attr_or(m1, m2, "is_manager")
                merge_attr_or(m1, m2, "notifications_enabled")

                m1.save()
                m2.delete()
            else:
                m2.person = p1
                m2.save()

        # for organizer configs, we are as careful as we were for memberships
        current_organizer_configs = p1.organizer_configs.select_for_update()
        organized_events = {o.event_id: o for o in current_organizer_configs}

        for o2 in p2.organizer_configs.select_for_update():
            if o2.event_id in organized_events:
                o1 = organized_events[o2.event_id]
                o1.created = min(o1.created, o2.created)
                merge_attr_or(o1, o2, "is_creator")
                merge_attr_or(o1, o2, "notifications_enabled")
                merge_attr_or(o1, o2, "as_group")

                o1.save()
                o2.delete()
            else:
                o2.person = p1
                o2.save()

        # we don't care as much for rsvps: reassign or delete is enough
        current_rsvps = p1.rsvps.select_for_update()
        rsvped_events = {r.event_id: r for r in current_rsvps}

        for r2 in p2.rsvps.all():
            if r2.event_id in rsvped_events:
                r2.delete()
            else:
                r2.person = p1
                r2.save()

        # we reassign email addresses as well

        # use list to make sure the querysets are evaluated now, before modifying the addresses
        email_order_1 = list(p1.get_personemail_order())
        email_order_2 = list(p2.get_personemail_order())
        for e2 in p2.emails.all():
            e2.person = p1
            e2.save()
        # and set back the order
        p1.set_personemail_order(email_order_1 + email_order_2)

        # We reassign simply for these categories
        p2.form_submissions.update(person=p1)
        p2.payments.update(person=p1)
        p2.event_images.update(author=p1)

        # we reassign poll choices only if p1 has not voted yet
        p1_votes = set(pc.poll_id for pc in p1.poll_choices.all())
        p2.poll_choices.exclude(poll_id__in=p1_votes).update(person=p1)

        # then we need to delete the second person, before removing it from mailtrain
        p2.delete()
