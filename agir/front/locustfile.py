from locust import TaskSet, task


class FrontTaskSet(TaskSet):
    @task
    def interrompre(self):
        self.interrupt()

    @task(2)
    def dashboard(self):
        self.client.get("/")
        self.client.get("/api/evenements/rsvped/")
        self.client.get("/api/evenements/suggestions/")
        self.client.get("/api/session")

    @task(2)
    def groupes(self):
        self.client.get("/mes-groupes/")
        self.client.get("/api/groupes/")
        self.client.get("/api/session/")
        self.client.get("/carte/groupes")
