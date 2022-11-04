import locale
from collections import Counter
from functools import partial
from pathlib import Path
from urllib.parse import urlencode

import beautifultable
import numpy as np
import pandas as pd
import requests
import yaml
from django.core.mail import get_connection
from django.core.management import BaseCommand
from django.db import transaction
from django.template import Template, Context
from django.utils import timezone
from tqdm import tqdm

from agir.events.models import Event, RSVP
from agir.lib.mailing import send_message
from agir.lib.utils import generate_token_params, grouper
from agir.people.models import Person, PersonTag

RED = "91"
GREEN = "92"

COLORED_TEXT = "\033[{color}m{text}\033[0m"

EMAILS_BY_CONNECTION = 500


def colored_text(text, color):
    return COLORED_TEXT.format(color=color, text=text)


def color_to(df, column, mask, color):
    df.loc[mask, column] = df.loc[mask, column].map(partial(colored_text, color=color))


def count_by(df, by):
    return df.groupby(["college"])[by].sum().astype(int)


def df_to_table(df, columns=None, colors=True):
    table = beautifultable.BeautifulTable(maxwidth=160)

    df = df.reset_index().copy()

    reached_target = df["subscribed"] == df["targets"]
    exceeded_target = df["subscribed"] > df["targets"]
    missing_candidates = df["available"] < df["to_draw"]
    too_many_actives = df["active"] > df["adjusted"]
    issue = missing_candidates | exceeded_target | too_many_actives | missing_candidates

    if colors:
        color_to(df, "college", issue, RED)
        color_to(df, "college", reached_target & ~issue, GREEN)
        color_to(df, "available", missing_candidates, RED)
        color_to(df, "subscribed", reached_target, GREEN)
        color_to(df, "subscribed", exceeded_target, RED)
        color_to(df, "active", too_many_actives, RED)
        color_to(df, "to_draw", missing_candidates, RED)

    if columns is not None and len(columns) > 0:
        df = df[["college"] + columns]

    for tup in df.itertuples(index=False):
        table.rows.append(tup)

    table.columns.header = columns or list(df.columns)

    return str(table)


def get_current_status(config):
    status = pd.read_csv(
        config["status_file"], parse_dates=["subscribe_limit"], index_col="order"
    )

    try:
        with open(config["email_sent_file"]) as f:
            email_sent = f.read().split()
    except FileNotFoundError:
        email_sent = []

    if status.subscribe_limit.dt.tz is None:
        status["subscribe_limit"] = status.subscribe_limit.dt.tz_localize(
            timezone.get_default_timezone()
        )

    event = Event.objects.get(pk=config["event_id"])

    all_persons = {
        str(uuid)
        for uuid in Person.objects.filter(id__in=status["id"]).values_list(
            "id", flat=True
        )
    }

    tag_unable = PersonTag.objects.get(label=f"{config['tag_prefix']} - renoncé")
    tag_designated = PersonTag.objects.get(label=f"{config['tag_prefix']} - nommé")
    subscribed_ids = [
        str(id)
        for id in Person.objects.filter(
            rsvps__event=event,
            rsvps__status__in=[RSVP.STATUS_AWAITING_PAYMENT, RSVP.STATUS_CONFIRMED],
        )
        .exclude(tags=tag_designated)
        .values_list("id", flat=True)
    ]
    unable_ids = [
        str(id) for id in tag_unable.people.all().values_list("id", flat=True)
    ]
    designated_ids = [
        str(id) for id in tag_designated.people.all().values_list("id", flat=True)
    ]

    now = timezone.now().astimezone(timezone.get_default_timezone())

    status["_exists"] = status.id.isin(all_persons)
    status["_drawn"] = status.subscribe_limit.notnull()
    status["_subscribed"] = status.id.isin(subscribed_ids)
    status["_designated"] = status.id.isin(designated_ids)
    status["_unable"] = status.id.isin(unable_ids)
    status["_active"] = (
        status._exists
        & ~status._subscribed
        & ~status._unable
        & (status.subscribe_limit > now)
    )
    status["_email_envoye"] = status.id.isin(email_sent)
    status["_available"] = status._exists & status.subscribe_limit.isnull()

    return status


def get_stats(status, config):
    now = timezone.now().astimezone(timezone.get_default_timezone())

    colleges = pd.Index(config["targets"].keys(), name="college")

    res = pd.DataFrame(
        {
            "targets": pd.Series(config["targets"]),
            "drawn": count_by(status, "_drawn"),
            "subscribed": count_by(status, "_subscribed"),
            "active": count_by(status, "_active"),
            "available": count_by(status, "_available"),
        },
        index=colleges,
    ).fillna(0, downcast="infer")

    res["refused"] = res["drawn"] - res["subscribed"] - res["active"]

    res = res.reindex(
        columns=["available", "targets", "drawn", "subscribed", "refused", "active"]
    )

    final_status = status[status.subscribe_limit < now]  # potentiellement vide
    final_subscribed = (
        count_by(final_status, "_subscribed")
        .reindex(index=colleges)
        .fillna(0, downcast="infer")
    )
    final_drawn = (
        count_by(final_status, "_drawn")
        .reindex(index=colleges)
        .fillna(0, downcast="infer")
    )

    res["needed"] = res["targets"] - res["subscribed"]
    res.loc[res["needed"] < 0, "needed"] = 0  # évitons les catastrophes

    res["final"] = final_subscribed.map(str) + " / " + final_drawn.map(str)

    if config.get("subscription_prior") and config.get("ignore_actual_rate"):
        res["adjusted"] = np.floor(res["needed"] / config["subscription_prior"]).astype(
            int
        )
    elif config.get("subscription_prior"):
        # On utilise un modèle bayésien simple :
        # - on considère que chaque tirage au sort est une variable de Bernoulli : soit la personne
        #   accepte, avec une probabilité `p`, soit elle refuse, avec une probabilité `1-p`
        # - on cherche donc à estimer, pour chaque collège, la valeur de cette probabilité `p`.
        #
        # On choisit donc comme prior pour `p` une distribution Beta, car il s'agit de la distribution
        # conjuguée de la distribution de Bernoulli, ce qui rend la mise à jour du prior très simple.
        from scipy.stats import beta

        # On utilise les deux paramètres `subscription_prior` et `prior_weight`  pour paramétrer cette
        # distribution a priori et obtenir les paramètres classiques `a` et `b`
        subscription_prior = config["subscription_prior"]
        prior_weight = config.get("subscription_prior_weight", 5)
        a = subscription_prior * prior_weight
        b = (1 - subscription_prior) * prior_weight
        # Dit autrement, `subscription_prior` est la moyenne souhaitée pour la distribution a priori,
        # et prior_weight donne le nombre d'essais réels qu'il faudra effectuer pour que l'information
        # obtenue "compte autant" dans la distribution a posteriori que notre prior.

        # Toutefois, ce qui nous intéresse in fine, c'est le nombre de personnes à tirer pour espérer remplir
        # l'objectif, sans néanmoins risquer de le dépasser. Si on suppose que le taux réel est de `p`, il faudrait
        # tirer en moyenne 1/p fois notre objectif final pour faire le nombre d'inscriptions prévu.

        # Comme on a pas le taux réel, et pour limiter les risques, on prend le 95ème centile que nous donne
        # notre distribution a posteriori : dit autrement, on estime qu'il y a 95 % de chances que le taux
        # réel de réponse positive soit pire que ce taux, compte tenu de notre prior et des réponses déjà observées.
        # Il s'agit donc en quelque sorte d'une "borne maximum" (à 95 %) sur la valeur du taux réel.
        estimated_maximum_rate = pd.Series(
            {
                college: beta.ppf(0.95, a=a + sub, b=b + drawn - sub)
                for college, (sub, drawn) in pd.concat(
                    [final_subscribed, final_drawn], axis=1
                ).iterrows()
            }
        )

        # On décide donc de tirer le nombre de personnes qu'il faudrait _en moyenne_ pour remplir la salle, si notre
        # borne maximale était le taux réel.
        res["acceptance_rate"] = (
            (final_subscribed / final_drawn).map("{:.3f}".format)
            + " (95 % < "
            + estimated_maximum_rate.map("{:.3f}".format)
            + ")"
        )
        res["adjusted"] = np.floor(res["needed"] / estimated_maximum_rate).astype(int)
    else:
        res["adjusted"] = res["needed"]

    res["to_draw"] = res["adjusted"] - res["active"]
    res.loc[res["to_draw"] < 0, "to_draw"] = 0  # évitons les catastrophes

    return res


def config_file(string):
    p = Path(string)

    with p.open("r") as c:
        config = yaml.load(c, Loader=yaml.SafeLoader)

    current_dir = p.parent

    for k in ["status_file", "email_html_file", "email_text_file", "email_sent_file"]:
        if k in config:
            config[k] = Path(config[k])
            if not config[k].is_absolute():
                config[k] = current_dir / config[k]

    return config


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("config", type=config_file)
        subparsers = parser.add_subparsers(
            title="Commandes",
            description="Les différentes commandes disponibles.",
            help="La commande à effectuer",
        )

        status_parser = subparsers.add_parser(
            "status", help="Afficher le statut actuel", aliases=["s"]
        )
        status_parser.add_argument("-c", "--columns", nargs="+", dest="columns")
        status_parser.add_argument("--no-color", action="store_false", dest="colors")
        status_parser.set_defaults(command=self.print_stats)

        update_parser = subparsers.add_parser(
            "update",
            help="Mettre à jour les statuts et envoyer les emails",
            aliases=["u"],
        )
        update_parser.add_argument(
            "-f", "--fake-it", action="store_false", dest="do_it"
        )
        update_parser.add_argument("-c", "--college")
        update_parser.set_defaults(command=self.update_and_draw)

        refresh_email_parser = subparsers.add_parser(
            "download-email", help="(re)télécharger l'email", aliases=["re"]
        )
        refresh_email_parser.set_defaults(command=self.download_email)

    def handle(self, *args, config, command, verbosity, **options):
        self.verbosity = verbosity
        return command(config, **options)

    def print_stats(self, config, columns=None, colors=False, **options):
        status = get_current_status(config)

        self.stdout.write(
            f"Pour le moment : {status._drawn.sum()} tirés, {status._subscribed.sum()} inscrits.\n"
        )

        stats = get_stats(status, config)
        self.stdout.write(df_to_table(stats, columns, colors))
        self.stdout.write("\n")

    def download_email(self, config, **options):
        r = requests.get(config["email_link"])
        with open(config["email_html_file"], "wb") as f:
            f.write(r.content)

    def update_and_draw(self, config, do_it=False, college=None, **options):
        status = get_current_status(config)
        stats = get_stats(status, config)

        new_draws = status.id.isin(
            [
                id
                for name, g in status[status._available].groupby(["college"])
                for id in g["id"].iloc[: stats.loc[name, "to_draw"]]
            ]
        )

        if college is not None:
            new_draws &= status.college == college

        # obligé de passer par UTC sinon Pandas fait chier :(
        limit = (
            pd.Timestamp(
                timezone.now() + timezone.timedelta(hours=config["subscribe_period"])
            )
            .astimezone(status.subscribe_limit.dt.tz)
            .replace(minute=0, second=0, microsecond=0)
        )

        status.loc[new_draws, "subscribe_limit"] = limit
        status.loc[new_draws, "_active"] = True

        if self.verbosity >= 1:
            drawn_counts = Counter(status.loc[new_draws, "college"])
            if drawn_counts:
                self.stdout.write("Tirage :\n")
                for g, c in drawn_counts.items():
                    self.stdout.write(f"{g}: {c} personnes\n")

        tag_current = PersonTag.objects.get(label=f"{config['tag_prefix']} - ouvert")

        if do_it:
            if new_draws.sum():
                status[[c for c in status.columns if not c.startswith("_")]].to_csv(
                    config["status_file"]
                )

            with transaction.atomic():
                # on met à jour le tag, ce qui retire l'accès à ceux qui ont dépassé leur période d'inscription
                # et l'ouvre aux nouveaux tirés
                tag_current.people.set(status.loc[status._active, "id"])

            self.send_emails(config, status)

    def send_emails(self, config, status):
        sending = status._active & ~status._email_envoye

        if self.verbosity >= 1 and sending.sum():
            self.stdout.write(f"{sending.sum()} emails à envoyer.\n")

        persons = {
            str(p.id): p
            for p in Person.objects.filter(id__in=status.loc[sending, "id"])
        }

        with open(config["email_html_file"]) as f:
            html_template = Template(f.read())
        with open(config["email_text_file"]) as f:
            text_template = Template(f.read())

        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

        with open(config["email_sent_file"], mode="a") as f:
            for g in grouper(
                tqdm(
                    status.loc[sending].itertuples(), total=sending.sum(), disable=None
                ),
                EMAILS_BY_CONNECTION,
            ):
                connection = get_connection()
                with connection:
                    for i, row in enumerate(g):
                        person = persons[row.id]

                        context = Context(
                            {
                                "email": person.email,
                                "login_query": urlencode(generate_token_params(person)),
                                "limit_time": row.subscribe_limit.strftime(
                                    "%A %d %B avant %Hh"
                                ),
                            }
                        )

                        html_message = html_template.render(context)
                        text_message = text_template.render(context)

                        send_message(
                            subject=config["email_subject"],
                            from_email=config.get(
                                "email_from",
                                "La France insoumise <nepasrepondre@lafranceinsoumise.fr>",
                            ),
                            text=text_message,
                            html=html_message,
                            to=[person.email],
                            connection=connection,
                        )

                        f.write(f"{row.id}\n")
                        f.flush()
