import requests
import uuid
import json

API_URL = "http://localhost:8000".rstrip('/')

class Experiment:
    def __init__(self, api_key, project_name):
        self.project_name = project_name
        self.api_key = api_key
        self.experiment_id = self._start_experiment()

    def _start_experiment(self):
        post_data = {
            "project_name": self.project_name,
        }
        headers = {
            "Content-Type": "application/json",
            'Authorization': f"Bearer {self.api_key}"
        }
        response = requests.post(
            url=f"{API_URL}/api/experiment/start/",
            data=json.dumps(post_data),
            headers=headers
        )
        if response.status_code != 200:
            raise Exception("Failed to start experiment")

        response_json = response.json()
        return response_json.get("experiment_key")

    def log_parameter(self, name, value):
        data = {
            "experiment_key": self.experiment_id,
            "parameter_name": name,
            "parameter_value": value
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.patch(
            url=f"{API_URL}/api/experiment/log-parameter/",
            data=json.dumps(data),
            headers=headers
        )
        if response.status_code != 200:
            raise Exception("Failed to log parameter")

if __name__ == "__main__":
    api_key = "2904e64c-eab8-4c3a-ba42-c5566d4fa229"
    project_name = "test"
    experiment = Experiment(api_key, project_name)
    experiment.log_parameter("test", "test")
