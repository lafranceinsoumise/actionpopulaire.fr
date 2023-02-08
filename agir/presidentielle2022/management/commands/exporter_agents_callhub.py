import logging

import asks
import tenacity
import trio
from agir.people.models import PersonEmail
from asks.errors import AsksException
from django.conf import settings
from django.db.models import Subquery, OuterRef, F
from django.utils.text import slugify

from agir.lib.management_utils import LoggingCommand
from agir.people.person_forms.models import PersonForm


logger = logging.getLogger(__name__)

RATE_LIMIT = 13
CONCURRENT_REQUESTS = 15
HTTP_TIMEOUT = 15
MAX_RETRIES = 10

OUTREMER = {
    "971": "ZA",
    "972": "ZB",
    "973": "ZC",
    "974": "ZD",
    "976": "ZM",
    "988": "ZN",
    "987": "ZP",
    "975": "ZS",
    "986": "ZW",
    "977": "ZX",
    "978": "ZX",
}


class TrioTokenBucket:
    """TokenBucket fonctionnel pour une utilisation avec une event loop"""

    def __init__(self, capacity, rate):
        self.capacity = self._last_value = capacity
        self._last_ts = trio.current_time()
        self.rate = rate

    async def take(self, c=1):
        """Cette version applique de facto une logique FIFO"""
        n = trio.current_time()
        v = min(self._last_value + self.rate * (n - self._last_ts), self.capacity) - c

        self._last_ts, self._last_value = n, v

        if v < 0:
            await trio.sleep(-v / self.rate)


class Command(LoggingCommand):
    def add_arguments(self, parser):
        parser.add_argument("form_slug")

    def handle(self, *args, form_slug, **options):
        form = PersonForm.objects.get(slug=form_slug)

        ps = (
            form.submissions.all()
            .annotate(
                email=Subquery(
                    PersonEmail.objects.filter(person__form_submissions=OuterRef("id"))
                    .order_by("_bounced", "_order")
                    .values("address")[:1]
                )
            )
            .values(
                "data",
                "email",
                "person_id",
                first_name=F("person__first_name"),
                last_name=F("person__last_name"),
            )
            .order_by("person_id", "-created")
            .distinct("person_id")
        )

        agents = [self.agent(p) for p in ps]

        trio.run(self.main, agents)

    @tenacity.retry(
        sleep=trio.sleep,
        wait=tenacity.wait_random_exponential(),
        stop=tenacity.stop_after_attempt(MAX_RETRIES),
        retry=tenacity.retry_if_exception_type((trio.TooSlowError, AsksException)),
    )
    async def request(self, method, path, raise_for_status=True, **kwargs):
        await self.bucket.take()
        with trio.fail_after(HTTP_TIMEOUT):
            r = await self.session.request(method, path=path, **kwargs)
            if raise_for_status:
                r.raise_for_status()
            return r

    def temps_estime(self, nb_requetes):
        """Retourne le temps estimé en minutes pour exécuter un certain nombre de requêtes"""
        sec = nb_requetes / self.bucket.rate

        if sec < 120:
            return f"{sec} secondes"

        return f"{round(sec / 60)} minutes"

    def agent(self, s):
        numero = int.from_bytes(s["person_id"].bytes[:4], "big")
        first_name = s.get("first_name", s["data"].get("first_name", ""))
        last_name = s.get("last_name", s["data"].get("last_name", ""))
        if first_name or last_name:
            username = f"{first_name[0].lower()}{last_name}"
        else:
            username = s["email"].split("@")[0].lower()
        return {
            "username": f"{slugify(username)}{numero}",
            "email": s["email"],
            "team": self.equipe_agent(s["data"]["departement"]),
        }

    def equipe_agent(self, d):
        if d in OUTREMER:
            return f"Département {OUTREMER[d]}"
        return f"Département {d}"

    async def recuperer_equipes(self):
        await self.bucket.take()
        res = await self.request("get", "/teams/")
        nb_equipes = res.json()["count"]

        nb_pages = (nb_equipes - 1) // 10 + 1
        logger.info(
            f"{nb_equipes} équipes existantes à récupérer, délai estimé : {self.temps_estime(nb_pages)}"
        )

        equipes = {}

        async def request_page(page, *, task_status):
            async with self.conn_capacity:
                task_status.started()
                res = await self.request("get", "/teams/", params={"page": page})
                for e in res.json()["results"]:
                    equipes[e["name"]] = e

        async with trio.open_nursery() as nursery:
            for page in range(1, nb_pages + 1):
                await nursery.start(request_page, page)

        return equipes

    async def recuperer_agents_existants(self):
        await self.bucket.take()
        res = await self.request("get", "/agents/")
        nb_agents = res.json()["count"]

        nb_pages = (nb_agents - 1) // 10 + 1
        logger.info(
            f"{nb_agents} agents existants à récupérer, délai estimé : {self.temps_estime(nb_pages)}"
        )

        existing_agents = set()

        async def request_page(page, *, task_status):
            # on prend une unité dans le bloc de capacité, et après seulement on indique avoir démarré
            async with self.conn_capacity:
                task_status.started()
                res = await self.request("get", "/agents/", params={"page": page})
                existing_agents.update(
                    agent["email"] for agent in res.json()["results"]
                )

        async with trio.open_nursery() as nursery:
            for page in range(1, nb_pages + 1):
                await nursery.start(request_page, page)

        return existing_agents

    async def creer_agent(self, agent, *, task_status):
        async with self.conn_capacity:
            task_status.started()
            res = await self.request(
                "post", "/agents/", data=agent, raise_for_status=False
            )
            if res.status_code == 400 and "username" in res.json():
                logger.debug(
                    f"Agent pour l'adresse {agent['email']} déjà en cours d'activation"
                )
            elif res.status_code == 201:
                logger.debug(f"Agent pour l'adresse {agent['email']} créé.")
            else:
                logger.warning(
                    f"Réponse étrange pour {agent['email']} : {res.status_code} - {res.text}"
                )

    async def main(self, agents):
        self.session = asks.Session(
            connections=CONCURRENT_REQUESTS,
            headers={"Authorization": f"Token {settings.CALLHUB_API_KEY}"},
            base_location=settings.CALLHUB_API_DOMAIN,
            endpoint="/v1/",
        )
        # Callhub limite à 13 requêtes par seconde, on prend une mini-marge.
        self.bucket = TrioTokenBucket(5, RATE_LIMIT)
        self.conn_capacity = trio.CapacityLimiter(CONCURRENT_REQUESTS)

        equipes = await self.recuperer_equipes()
        for a in agents:
            if a["team"] not in equipes:
                logger.info(f"Équipe {a['team']} inexistante.")

        agents = [a for a in agents if a["team"] in equipes]

        existants = await self.recuperer_agents_existants()
        a_ajouter = [a for a in agents if a["email"] not in existants]
        logger.info(
            f"{len(a_ajouter)} agents à ajouter. Délai estimé {self.temps_estime(len(a_ajouter))}."
        )

        async with trio.open_nursery() as nursery:
            for a in a_ajouter:
                await nursery.start(self.creer_agent, a)
