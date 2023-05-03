# This should include the class Experiment, which is the main class for
# tracking experiments. The Experiment class should be similar to the
# comet.ml Experiment class. It should have the following methods:
# - init: initialize the experiment
import requests
import uuid
import json


class Experiment():

    def __init__(self, api_key, project_name):
        self.project_name = project_name
        self.api_key = api_key
        self.id = uuid.uuid4().hex

        # Report the start of the experiment to REST API
        self.report_experiment_start()

    def report_experiment_start(self):
        # Send a request to the REST API to report the start of the experiment
        post_data = {
            "project_name": self.project_name,
            "experiment_key": self.id
        }

        headers = {
            "Content-Type": "application/json",
            'Authorization': f"Bearer {self.api_key}"
        }
        response = requests.post(
            url="http://localhost:8000/api/experiment/start/",
            data=json.dumps(post_data),
            headers=headers
        )

        if response.status_code != 200:
            raise Exception("Failed to report experiment start to REST API")
        
        # Read in page_id from response
        response_json = response.json()
        self.id = response_json["page_id"]


    # I couldn't test this because the access token is not working
    def log_parameter(self, name, value):
        data = {
            "experiment_key": self.id,
            "parameter_name": name,
            "parameter_value": value
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.patch(
            url="http://localhost:8000/api/experiment/log-parameter/",
            data=json.dumps(data),
            headers=headers
        )
        if response.status_code != 200:
            raise Exception("Failed to log parameter to REST API")


if __name__ == "__main__":
    experiment = Experiment("2904e64c-eab8-4c3a-ba42-c5566d4fa229", "test")
    experiment.log_parameter("test", "test")
