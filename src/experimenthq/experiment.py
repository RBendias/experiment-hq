from typing import List, Optional
import queue
import threading

import requests

from experimenthq.notion_types import NotionTypes

API_URL = "https://www.api.experiment-hq.com/"
NOTION_BASE_URL = "https://www.notion.so/"


class Experiment:
    """
    Experiment class for logging parameters to Notion.

    args:
        api_key (str): API key for the ExperimentHQ API
        project (str): Name of the project to log to
        name (Optional[str]): Name of the experiment
        description (Optional[str]): Description of the experiment
        tags (Optional[List[str]]): List of tags to add to the experiment
    """

    def __init__(
        self,
        api_key: str,
        project: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.project = project
        self.api_key = api_key
        self.name = name
        self.description = description
        self.tags = tags
        self.session = requests.Session()
        self.experiment_id = self._start_experiment()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self) -> None:
        while True:
            task = self.queue.get()
            if task is None:  # We use None as a sentinel to end the thread.
                break
            data, headers = task
            try:
                response = self.session.post(
                    f"{API_URL}experiments/{self.experiment_id}/parameters",
                    json=data,
                    headers=headers,
                )

                if response.status_code not in {200, 401, 400, 404}:
                    print(
                        f"Warning: Failed to log parameter `{data['parameter_name']}` with "
                        f"value: `{data['parameter_value']}`. Please add it manually to the "
                        f"corresponding Notion page: {NOTION_BASE_URL+self.experiment_id}."
                    )
            finally:
                self.queue.task_done()

    def _start_experiment(self) -> str:
        post_data = {
            "project": self.project,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        response = self.session.post(
            f"{API_URL}experiments",
            json=post_data,
            headers=headers,
        )
        if response.status_code == 401:
            raise Exception("Invalid API key")
        elif response.status_code == 403:
            raise Exception("Maximum number of experiments reached")
        elif response.status_code == 404:
            raise Exception("ExperimentHQ database not found")
        elif response.status_code != 200:
            raise Exception("Failed to start experiment with message: " + response.text)
        return response.json().get("experiment_id")

    def log_parameter(
        self,
        name: str,
        value: str,
        notion_type: Optional[str] = None,
    ) -> None:
        """
        Log a parameter to Notion.

        args:
            name (str): Name of the parameter
            value (str): Value of the parameter. Depending on the type of the parameter,
                         there needs to be a specific format. Please pass several values
                         for multi_select parameters as one string separated by commas.
                         The date needs to be in ISO #8601 format and the people parameter
                         needs to be a Notion ID.
            notion_type Optional(str): Used to create a new column in the Notion database.
                                       Setting `notion_type` is optional and will be ignored
                                        if the column already exists. If the column should be
                                        created with a specific type, the following types are
                                        supported:
                                            - rich_text
                                            - number
                                            - select
                                            - multi_select
                                            - files
                                            - checkbox
                                            - url
                                            - email
                                            - phone_number
                                            - people
                                            - date
        """
        # Check if the value is valid:
        if notion_type is not None:
            NotionTypes(notion_type).validate_value(
                value=value,
                notion_type=notion_type,
            )

        data = {
            "parameter_name": name,
            "parameter_value": value,
            "parameter_type": notion_type,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Enqueue the task instead of executing it immediately
        self.queue.put((data, headers))
