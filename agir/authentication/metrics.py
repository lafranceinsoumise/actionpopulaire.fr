from prometheus_client import Counter

logged_in = Counter("agir_auth_logged_in", "Connexions réussies", ["backend"])
logged_out = Counter("agir_auth_logged_out", "Déconnexions")
login_failed = Counter("agir_auth_login_failed", "Connexions échouées", ["backend"])
