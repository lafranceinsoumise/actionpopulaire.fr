import ipaddress
import random

from locust import between
from pyquery import PyQuery

from agir.front.locustfile import FrontTaskSet
from agir.lib.locust_utils import AgirHttpUser

MAX_ACCOUNTS = 1000


class ConnectedUser(AgirHttpUser):
    wait_time = between(1, 2)

    tasks = {FrontTaskSet: 1}

    def on_start(self):
        self.wait()  # pour que tous les utilisateurs n'arrivent pas au même moment

        self.ip = self.choose_ip()
        self.email = self.choose_email()
        self.headers.update({"X-Forwarded-For": self.ip})

        self.connect()

    def choose_email(self):
        return f"locust{random.randrange(0, MAX_ACCOUNTS)}@loadtest.com"

    def connect(self):
        with self.client.get("/connexion/", catch_response=True) as res:
            pq = PyQuery(res.text)
            csrf_token = pq('input[name="csrfmiddlewaretoken"]').attr("value")
            if not csrf_token:
                res.failure("Impossible de récupérer le csrfmiddlewaretoken")
                return res.stop()

        with self.client.post(
            "/connexion/",
            data={"csrfmiddlewaretoken": csrf_token, "email": self.email},
            catch_response=True,
            allow_redirects=False,
        ) as res:
            if res.status_code != 302 or not res.headers["Location"].endswith(
                "/connexion/code/"
            ):
                res.failure("Pas redirigé vers la page de saisie du code")
                return self.stop()
        self.wait()

        with self.client.get("/connexion/code/", catch_response=True) as res:
            pq = PyQuery(res.text)
            csrf_token = pq('input[name="csrfmiddlewaretoken"]').attr("value")
            code = pq("span.logincode").text()

            if not csrf_token or not code:
                res.failure("Code de connexion non reçu.")
                return self.stop()

        with self.client.post(
            "/connexion/code/",
            data={"csrfmiddlewaretoken": csrf_token, "code": code},
            catch_response=True,
            allow_redirects=False,
        ) as res:
            if res.status_code != 302:
                res.failure("Impossible de se connecter")
                return self.stop()

    def choose_ip(self):
        subnet = ipaddress.ip_network("10.0.0.0/8")
        bits = random.getrandbits(subnet.max_prefixlen - subnet.prefixlen)
        addr = ipaddress.IPv4Address(subnet.network_address + bits)

        return str(addr)
