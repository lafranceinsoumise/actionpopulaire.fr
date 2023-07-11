from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError

__all__ = ["merge_persons"]

from agir.elus.models import AccesApplicationParrainages
from agir.people.models import Person


def _set_or_fields(o1, o2, attr, default=None):
    return setattr(o1, attr, getattr(o1, attr, None) or getattr(o2, attr, default))


# GENERIC MERGING STRATEGIES
def merge_nullable(p1, p2, field):
    # gère le cas particulier des valeurs « falsy » mais non `None`
    if getattr(p1, field.name, None) is not None:
        return
    setattr(p1, field.name, getattr(p2, field.name, None))


def merge_text_fields(p1, p2, field):
    _set_or_fields(p1, p2, field.name, default="")


def merge_boolean_field(p1, p2, field):
    _set_or_fields(p1, p2, field.name, default=False)


def merge_dicts(p1, p2, field):
    setattr(
        p1, field.name, {**getattr(p2, field.name, {}), **getattr(p1, field.name, {})}
    )


def merge_reassign_related(p1, p2, field):
    for rel_obj in getattr(p2, field.get_accessor_name()).all():
        try:
            with transaction.atomic():
                setattr(rel_obj, field.remote_field.name, p1)
                rel_obj.save(update_fields=[field.remote_field.name])
        except IntegrityError:
            # It means the related object exists, in a sense, on p1 already
            # we don't need to do anything for this related object
            continue


def merge_with_priority_ordering(order):
    order = list(order)

    def merge_func(p1, p2, field):
        setattr(
            p1,
            field.name,
            min([getattr(p1, field.name), getattr(p2, field.name)], key=order.index),
        )

    return merge_func


# SPECIFIC MERGING STRATEGIES
def merge_newsletters(p1, p2, _field):
    p1.newsletters = list(set(p1.newsletters).union(p2.newsletters))


def merge_tags(p1, p2, _field):
    # copying person tags
    missing_tags = p2.tags.all().difference(p1.tags.all())
    p1.tags.add(*missing_tags)


def merge_muted_messages(p1, p2, _field):
    muted_messages = p2.messages_muted.all().difference(p1.messages_muted.all())
    p1.messages_muted.add(*muted_messages)


def merge_email_addresses(p1, p2, _field):
    # we reassign email addresses as well
    # use list to make sure the querysets are evaluated now, before modifying the addresses
    email_order_1 = list(p1.get_personemail_order())
    email_order_2 = list(p2.get_personemail_order())

    if not p1.public_email and p2.public_email:
        p2.public_email.person = p1
        p2.public_email.save()

    for e2 in p2.emails.all():
        e2.person = p1
        e2.save()
    # and set back the order
    p1.set_personemail_order(email_order_1 + email_order_2)


def merge_memberships(p1, p2, _field):
    # for memberships, we want to carefully copy the properties in case there is a duplicate
    current_memberships = p1.memberships.select_for_update()
    groups = {m.supportgroup_id: m for m in current_memberships}

    for m2 in p2.memberships.all():
        if m2.supportgroup_id in groups:
            m1 = groups[m2.supportgroup_id]
            m1.created = min(m1.created, m2.created)
            m1.membership_type = max(m1.membership_type, m2.membership_type)
            _set_or_fields(m1, m2, "notifications_enabled", default=False)

            m1.save()
            m2.delete()
        else:
            m2.person = p1
            m2.save()


def merge_rsvps(p1, p2, _field):
    # we don't care as much for rsvps: reassign or delete is enough
    current_rsvps = p1.rsvps.select_for_update()
    rsvped_events = {r.event_id: r for r in current_rsvps}

    for r2 in p2.rsvps.all():
        if r2.event_id in rsvped_events:
            r2.delete()
        else:
            r2.person = p1
            r2.save()


def merge_organizer_configs(p1, p2, _field):
    # for organizer configs, we are as careful as we were for memberships
    current_organizer_configs = p1.organizer_configs.select_for_update()
    organized_events = {o.event_id: o for o in current_organizer_configs}

    for o2 in p2.organizer_configs.select_for_update():
        if o2.event_id in organized_events:
            o1 = organized_events[o2.event_id]
            _set_or_fields(o1, o2, "is_creator", default=False)
            _set_or_fields(o1, o2, "notifications_enabled", default=False)
            _set_or_fields(o1, o2, "as_group", default=False)

            o1.save()
            o2.delete()
        else:
            o2.person = p1
            o2.save()


def merge_poll_choices(p1, p2, _field):
    # we reassign poll choices only if p1 has not voted yet
    p1_votes = set(pc.poll_id for pc in p1.poll_choices.all())
    p2.poll_choices.exclude(poll_id__in=p1_votes).update(person=p1)


def merge_comments(p1, p2, _field):
    p1.commentaires = f"{p1.commentaires}\n\n{p2.commentaires}".strip()


def merge_acces_application_parrainages(p1, p2, _field):
    try:
        ac2 = p2.acces_application_parrainages
    except AccesApplicationParrainages.DoesNotExist:
        return

    ac1, _created = AccesApplicationParrainages.objects.get_or_create(person=p1)

    ac1.etat = max(
        ac1.etat,
        ac2.etat,
        key=[
            AccesApplicationParrainages.Etat.EN_ATTENTE,
            AccesApplicationParrainages.Etat.REFUSE,
            AccesApplicationParrainages.Etat.VALIDE,
        ].index,
    )

    ac1.save()


def merge_event_speakers(p1, p2, _field):
    try:
        es2 = p2.event_speaker
    except ObjectDoesNotExist:
        return

    try:
        es1 = p1.event_speaker
    except ObjectDoesNotExist:
        es2.person_id = p1.id
        es2.save()
        return

    # If both people have a related event_speaker, combine es2 and es1 themes
    es1_themes = es1.event_themes.values_list("id", flat=True)
    for theme in es2.event_themes.exclude(id__in=es1_themes):
        es1.event_themes.add(theme)
    es2.delete()


MERGE_STRATEGIES = {
    # Many2one
    "form_submissions": merge_reassign_related,
    "emails": merge_email_addresses,
    "personvalidationsms": None,
    "events": None,
    "organized_events": None,
    "group_event_participation": None,
    "rsvps": merge_rsvps,
    "organizer_configs": merge_organizer_configs,
    "event_images": merge_reassign_related,
    "supportgroups": None,
    "memberships": merge_memberships,
    "supportgroupmessage": merge_reassign_related,
    "supportgroupmessagecomment": merge_reassign_related,
    "messages_muted": merge_muted_messages,
    "userreport": merge_reassign_related,
    "poll_choices": merge_reassign_related,
    "payments": merge_reassign_related,
    "subscriptions": merge_reassign_related,
    "activities": merge_reassign_related,
    "municipales2020_commune": None,
    "mandat_municipal": merge_reassign_related,
    "mandat_departemental": merge_reassign_related,
    "mandat_regional": merge_reassign_related,
    "mandat_consulaire": merge_reassign_related,
    "mandat_depute": merge_reassign_related,
    "mandat_depute_depute_europeen": merge_reassign_related,
    "campaignsentevent": None,
    "pushcampaignsentevent": None,
    "notification_subscriptions": None,
    # Simple fields
    "created": None,
    "modified": None,
    "id": None,
    "coordinates": merge_nullable,
    "coordinates_type": merge_text_fields,
    "location_name": merge_text_fields,
    "location_address1": merge_text_fields,
    "location_address2": merge_text_fields,
    "location_citycode": merge_nullable,
    "location_city": merge_text_fields,
    "location_zip": merge_text_fields,
    "location_state": merge_text_fields,
    "location_departement_id": merge_text_fields,
    "location_country": merge_text_fields,
    "role": None,
    "auto_login_salt": None,
    "is_insoumise": merge_boolean_field,
    "is_2022": merge_boolean_field,
    "membre_reseau_elus": merge_with_priority_ordering(
        [
            Person.MEMBRE_RESEAU_EXCLUS,
            Person.MEMBRE_RESEAU_OUI,
            Person.MEMBRE_RESEAU_NON,
            Person.MEMBRE_RESEAU_SOUHAITE,
            Person.MEMBRE_RESEAU_INCONNU,
        ]
    ),
    "newsletters": merge_newsletters,
    "subscribed_sms": merge_boolean_field,
    "event_notifications": merge_boolean_field,
    "group_notifications": merge_boolean_field,
    "draw_participation": merge_boolean_field,
    "first_name": merge_text_fields,
    "last_name": merge_text_fields,
    "contact_phone": merge_text_fields,
    "contact_phone_status": merge_with_priority_ordering(
        [
            Person.CONTACT_PHONE_VERIFIED,
            Person.CONTACT_PHONE_PENDING,
            Person.CONTACT_PHONE_UNVERIFIED,
        ]
    ),
    "gender": merge_text_fields,
    "date_of_birth": merge_nullable,
    "mandates": None,
    "meta": merge_dicts,
    "commentaires": merge_comments,
    "search": None,
    "tags": merge_tags,
    "referrer_id": None,
    "transferoperation": None,
    "display_name": merge_text_fields,
    "image": merge_text_fields,
    "rechercheparrainage": merge_reassign_related,
    "read_messages": merge_reassign_related,
    "depense": None,
    "acces_application_parrainages": merge_acces_application_parrainages,
    "invitation_response": merge_reassign_related,
    "invitation": merge_reassign_related,
    "candidature": merge_reassign_related,
    "_email": None,
    "voting_proxy": None,
    "polling_station_officer": None,
    "crp": merge_comments,
    "person_qualification": merge_reassign_related,
    "event_speaker": merge_event_speakers,
    "public_email": None,
    "action_radius": None,
    "document": merge_reassign_related,
}


def merge_persons(p1, p2):
    """Merge the two persons together, keeping p1 and deleting p2, associating all information linked to p2 to p1"""
    fields = Person._meta.get_fields()
    missing_fields = {f.name for f in fields}.difference(MERGE_STRATEGIES)
    unknown_fields = set(MERGE_STRATEGIES).difference({f.name for f in fields})

    if missing_fields or unknown_fields:
        message = []
        if missing_fields:
            message.append(f"Fields without strategy: {missing_fields!r}")
        if unknown_fields:
            message.append(f"Unknown fields' name: {unknown_fields!r}")

        raise AssertionError("\n".join(message))

    # check if it's not the same user
    if p1.pk == p2.pk:
        raise ValueError("Cannot merge a person instance with itself")

    with transaction.atomic():
        for f in fields:
            func = MERGE_STRATEGIES.get(f.name)
            if func is not None:
                func(p1, p2, f)

        p1.save()

        # finally we need to delete the second person
        p2.delete()
