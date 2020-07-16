from prometheus_client import Counter

logged_in = Counter("agir_people_logged_in", "Connexions réussies", ["backend"])
logged_out = Counter("agir_people_logged_out", "Déconnexions")
login_failed = Counter("agir_people_login_failed", "Connexions échouées", ["backend"])
