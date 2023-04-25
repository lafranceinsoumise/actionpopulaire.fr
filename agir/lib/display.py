import datetime
import string

from django.template.defaultfilters import floatformat
from django.utils.formats import date_format
from django.utils.html import format_html, format_html_join, mark_safe
from django.utils.timezone import utc, is_aware
from django.utils.translation import gettext as _, ngettext


def display_liststring(strings, sep=", ", last_sep=" et "):
    if len(strings) == 0:
        return ""

    return ngettext(
        _(strings[0]),
        _("{items} {last_sep} {last_item}").format(
            items=sep.join(strings[:-1]), last_item=strings[-1], last_sep=last_sep
        ),
        len(strings),
    )


def display_address(object):
    parts = []
    if getattr(object, "location_name", None):
        parts.append(format_html("<em>{}</em>", object.location_name))

    if object.location_address1:
        parts.append(object.location_address1)
        if object.location_address2:
            parts.append(object.location_address2)

    if object.location_state:
        parts.append(object.location_state)

    if object.location_zip and object.location_city:
        parts.append("{} {}".format(object.location_zip, object.location_city))
    else:
        if object.location_zip:
            parts.append(object.location_zip)
        if object.location_city:
            parts.append(object.location_city)

    if object.location_country and str(object.location_country) != "FR":
        parts.append(object.location_country.name)

    return format_html_join(mark_safe("<br/>"), "{}", ((part,) for part in parts))


def display_price(price, price_in_cents=True):
    """Représente correctement un prix exprimé comme un nombre entier de centimes

    Dans l'application, c'est notamment le cas pour tous les montants liés aux paiements,
    dons, souscriptions, etc.
    """
    if price_in_cents:
        price = price / 100
    return "{}\u00A0€".format(floatformat(price, 2))


def display_allocations(allocations):
    from agir.groups.models import SupportGroup
    from agir.donations.models import AllocationModelMixin
    from agir.donations.allocations import get_allocation_list

    strings = []
    for allocation in get_allocation_list(allocations):
        allocation_type = allocation.get("type")
        amount = allocation.get("amount")
        if allocation_type == AllocationModelMixin.TYPE_GROUP:
            group_id = allocation.get("group")
            try:
                group = SupportGroup.objects.get(pk=group_id)
                strings.append(f"{amount/100}€ vers {group.name}")
            except SupportGroup.DoesNotExist:
                strings.append(f"{amount/100}€ vers {group_id}")
        elif allocation_type == AllocationModelMixin.TYPE_DEPARTEMENT:
            departement = allocation.get("departement")
            strings.append(f"{amount / 100}€ vers le département {departement}")
        elif allocation_type == AllocationModelMixin.TYPE_CNS:
            strings.append(f"{amount / 100}€ vers la caisse nationale de solidarité")

    return display_liststring(strings)


def pretty_time_since(d, relative_to=None):
    """Convert datetime.date to datetime.datetime for comparison."""
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if relative_to and not isinstance(relative_to, datetime.datetime):
        relative_to = datetime.datetime(
            relative_to.year, relative_to.month, relative_to.day
        )

    relative_to = relative_to or datetime.datetime.now(utc if is_aware(d) else None)

    delta = relative_to - d
    delta_seconds = delta.days * 24 * 3600 + delta.seconds

    if delta.days > 365 and d.year != relative_to.year and d.month != relative_to.month:
        return _("en {:d} ou avant").format(d.year)
    elif delta.days > 30 and (d.month != relative_to.month):
        return _("en {} dernier").format(date_format(d, "F"))
    elif delta.days > 14:
        return _("il y a {:d} semaines").format(round(delta.days / 7))
    elif delta.days > 0 and d.day == relative_to.day - 1:
        return _("hier")
    elif delta.days > 0:
        num_days = round(delta_seconds / 3600 / 24)
        return ngettext("il y a %d jour", "il y a %d jours", num_days) % num_days
    elif delta_seconds > 3600:
        num_hours = round(delta_seconds / 3600)
        return ngettext("il y a %d heure", "il y a %d heures", num_hours) % num_hours
    elif delta_seconds > 60:
        num_seconds = round(delta_seconds / 60)
        return (
            ngettext("il y a %d minute", "il y a %d minutes", num_seconds) % num_seconds
        )
    else:
        return _("Il y a moins d'une minute")


def str_summary(text, length_max=500, last_word_limit=100):
    """limite un message en taille.

    Le message n'est pas coupé en plein milieu d'un mot, sauf si ce mot est plus long que `last_word_limit`
    '...' est ajouté à la fin de la chaîne."""
    text_len = len(text)
    if text_len > length_max:
        n = min(text_len, length_max)
        m = 0
        while text[n] not in string.whitespace and m <= last_word_limit:
            n -= 1
            m += 1
        text = text[0 : n + 1]
        if text_len > length_max:
            text += "..."
    return text


def genrer_mot_inclusif(mot, genre):
    if "⋅" not in mot or genre not in ["M", "F"]:
        return mot

    # on sépare la racine de la partie féminine
    racine, ext = mot.split("⋅", 1)

    # seules peuvent être déclinées automatiquement les mots dont la forme féminine finit par "e", éventuellement
    # au pluriel.
    if ext[-1] != "e" and ext[-2:] != "es":
        raise ValueError(
            "Seules les terminaisons en e ou es peuvent utiliser la forme à 2 arguments."
        )

    pluriel_commun = "s" if ext[-1:] == "s" and racine[-1] not in "sx" else ""
    if pluriel_commun:
        ext = ext[:-1]

    # l'heuristique utilisée part du principe que la terminaison féminine a généralement un caractère de plus que la
    # terminaison masculine. Surprenamment, ça marche dans un très grand nombre de cas.
    tronque = len(racine) - len(ext) + 1

    if genre == "M":
        return f"{racine}{pluriel_commun}"
    return f"{racine[:tronque]}{ext}{pluriel_commun}"


def genrer(genre, *args):
    """Genrer correctement une expression

    Il y a deux façons d'appeler cette fonction : avec 2 arguments, et avec 4.

    Le premier argument est toujours le genre de destination.

    Dans la version à deux arguments, le deuxième argument doit être un mot sous forme inclusive, écrit avec un
    point médian (par exemple "insoumis⋅e"), et il doit s'agir d'un mot dont la version féminine est en "e".
    Dans ces cas, la fonction est généralement capable de décliner le mot correspondant, mais peut échouer avec certains
    mots.

    Dans la version à 4 arguments, les 3 derniers arguments doivent être la forme masculine, féminine, et épicène, dans
    cet ordre.

    :param genre: le genre dans lequel il faut décliner le mot
    :param args: soit un unique argument sous forme inclusive (avec point médian), soit les formes masculine, féminine,
    et épicène, dans cet ordre
    :return: le mot décliné selon le bon genre
    """
    if len(args) not in (1, 3):
        raise TypeError

    if len(args) == 1:
        return " ".join(genrer_mot_inclusif(mot, genre) for mot in args[0].split())

    return args[0 if genre == "M" else 1 if genre == "F" else 2]
