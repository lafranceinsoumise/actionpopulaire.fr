from collections import Counter
from pathlib import Path

import locale
from urllib.parse import urlencode

import beautifultable
import pandas as pd
import numpy as np
import requests
import yaml
from django.core.mail import get_connection
from django.core.management import BaseCommand
from django.db import transaction
from django.template import Template, Context
from django.utils import timezone

from agir.events.models import Event
from agir.lib.mailing import send_mail
from agir.lib.utils import generate_token_params
from agir.people.models import Person, PersonTag


RED = "91"
GREEN = "92"

COLORED_TEXT = "\033[{color}m{text}\033[0m"


def colored_text(text, color):
    return COLORED_TEXT.format(color=color, text=text)


def count_by(df, by):
    return df.groupby(["gender"])[by].sum().astype(int)


def df_to_table(df):
    table = beautifultable.BeautifulTable(max_width=160)
    table.column_headers = [df.index.name] + list(df.columns)
    for tup in df.itertuples():
        table.append_row(tup)

    return table


def get_current_status(config):
    status = pd.read_csv(
        config["status_file"], parse_dates=["subscribe_limit"], index_col="order"
    )

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
    subscribed_ids = [
        str(id) for id in event.attendees.all().values_list("id", flat=True)
    ]
    unable_ids = [
        str(id) for id in tag_unable.people.all().values_list("id", flat=True)
    ]

    now = timezone.now().astimezone(timezone.get_default_timezone())

    status["_exists"] = status.id.isin(all_persons)
    status["_drawn"] = status.subscribe_limit.notnull()
    status["_subscribed"] = status.id.isin(subscribed_ids)
    status["_unable"] = status.id.isin(unable_ids)
    status["_active"] = (
        status._exists
        & ~status._subscribed
        & ~status._unable
        & (status.subscribe_limit > now)
    )
    status["_available"] = status._exists & status.subscribe_limit.isnull()

    return status


def get_stats(status, config):
    now = timezone.now().astimezone(timezone.get_default_timezone())

    res = pd.DataFrame(
        {
            "targets": pd.Series(config["targets"]),
            "drawn": count_by(status, "_drawn"),
            "subscribed": count_by(status, "_subscribed"),
            "active": count_by(status, "_active"),
            "available": count_by(status, "_available"),
        }
    ).fillna(0, downcast="infer")

    res["refused"] = res["drawn"] - res["subscribed"] - res["active"]

    res = res.reindex(
        columns=["available", "targets", "drawn", "subscribed", "refused", "active"]
    )

    final_status = status[status.subscribe_limit < now]
    final_subscribed = count_by(final_status, "_subscribed")
    final_drawn = count_by(final_status, "_drawn")

    res["needed"] = res["targets"] - res["subscribed"]
    res.loc[res["needed"] < 0, "needed"] = 0  # évitons les catastrophes

    res["final"] = final_subscribed.map(str) + " / " + final_drawn.map(str)

    if config.get("overdraw_rate"):
        from scipy.stats import beta

        overdraw = config["overdraw_rate"]

        a = 1
        b = (1 - overdraw) / overdraw

        overdraw_rate = pd.Series(
            {
                g: beta.ppf(0.95, a=a + sub, b=b + drawn - sub)
                for g, (sub, drawn) in pd.concat(
                    [final_subscribed, final_drawn], axis=1
                ).iterrows()
            }
        )

        res["acceptance_rate"] = (
            (final_subscribed / final_drawn).map("{:.3f}".format)
            + " (95 % < "
            + overdraw_rate.map("{:.3f}".format)
            + ")"
        )
        res["adjusted"] = np.floor(res["needed"] / overdraw_rate).astype(int)
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

    for k in ["status_file", "email_file"]:
        config[k] = current_dir / Path(config[k])

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
        status_parser.set_defaults(command=self.print_stats)

        update_parser = subparsers.add_parser(
            "update",
            help="Mettre à jour les statuts et envoyer les emails",
            aliases=["u"],
        )
        update_parser.add_argument(
            "-f", "--fake-it", action="store_false", dest="do_it"
        )
        update_parser.set_defaults(command=self.update_and_draw)

        refresh_email_parser = subparsers.add_parser(
            "download-email", help="(re)télécharger l'email", aliases=["re"]
        )
        refresh_email_parser.set_defaults(command=self.download_email)

    def handle(self, *args, config, command, verbosity, **options):
        self.verbosity = verbosity
        return command(config, **options)

    def print_stats(self, config, **options):
        status = get_current_status(config)

        print(
            f"Pour le moment : {status._drawn.sum()} tirés, {status._subscribed.sum()} inscrits."
        )

        stats = get_stats(status, config)
        print(df_to_table(stats))

    def download_email(self, config, **options):
        r = requests.get(config["email_link"])
        with open(config["email_file"], "wb") as f:
            f.write(r.content)

    def update_and_draw(self, config, do_it=False, **options):
        status = get_current_status(config)
        stats = get_stats(status, config)

        new_draws = status.id.isin(
            [
                id
                for name, g in status[status._available].groupby(["gender"])
                for id in g["id"].iloc[: stats.loc[name, "to_draw"]]
            ]
        )

        if new_draws.sum() == 0:
            return

        # obligé de passer par UTC sinon Pandas fait chier :(
        limit = (
            pd.Timestamp(
                timezone.now() + timezone.timedelta(hours=config["subscribe_period"])
            )
            .astimezone(status.subscribe_limit.dt.tz)
            .replace(minute=0, second=0, microsecond=0)
        )

        status.loc[new_draws, "subscribe_limit"] = limit

        if self.verbosity >= 1:
            drawn_counts = Counter(status.loc[new_draws, "gender"])
            print("Tirage :")
            for g, c in drawn_counts.items():
                print(f"{g}: {c} personnes")

        if do_it:
            status[[c for c in status.columns if not c.startswith("_")]].to_csv(
                config["status_file"]
            )

        tag_current = PersonTag.objects.get(label=f"{config['tag_prefix']} - ouvert")

        active_persons = {
            str(p.id): p
            for p in Person.objects.filter(
                id__in=status.loc[status._active | new_draws, "id"]
            )
        }

        if do_it:
            with transaction.atomic():
                # on retire la possibilité de s'inscrire aux précédents
                tag_current.people.remove(*tag_current.people.all())

                # on ajoute les nouveaux aux deux tags
                tag_current.people.add(
                    *status.loc[status._active | new_draws, "id"].map(active_persons)
                )

        with open(config["email_file"]) as f:
            template_content = f.read()

        template = Template(template_content)
        connection = get_connection()

        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

        with connection:
            for i, row in enumerate(status.loc[new_draws].itertuples()):
                person = active_persons[row.id]

                html_message = template.render(
                    Context(
                        {
                            "email": person.email,
                            "login_query": urlencode(generate_token_params(person)),
                            "limit_time": row.subscribe_limit.strftime(
                                "%A %d %B avant %Hh"
                            ),
                        }
                    )
                )

                print(row.gender, end="\n" if i % 80 == 79 else "", flush=True)

                if do_it:
                    send_mail(
                        subject=config["email_subject"],
                        html_message=html_message,
                        from_email=config.get("email_from", "La France insoumise <nepasrepondre@lafranceinsoumise.fr>"),
                        recipient_list=[person],
                        connection=connection,
                    )
        print()  # newline
