from locust import HttpUser, task, between
import json

class WebSocketUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def connect_ws(self):
        with self.client.websocket("/ws/stream") as ws:
            ws.send("ping")
            res = ws.recv()
            assert res == "pong"
