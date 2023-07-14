import time
from typing import Dict, List, Optional, Union
import queue
import threading
import atexit


import requests

from experimenthq.notion_types import NotionTypes

API_URL = "https://www.api.experiment-hq.com/"
NOTION_BASE_URL = "https://www.notion.so/"

MAX_RETRIES = 3
RETRY_DELAY = 1

experiment = None


def get_global_experiment() -> object:
    """Gets the global experiment.

    Returns:
        The global experiment.
    """
    global experiment
    return experiment


def set_global_experiment(new_experiment: object) -> None:
    """Sets the global experiment.

    Args:
        new_experiment: The new global experiment to set.
    """
    global experiment
    experiment = new_experiment


class Experiment:
    """A class for logging parameters to Notion.

    Attributes:
        api_key (str): The API key for the ExperimentHQ API.
        project (str): The name of the project to log to.
        name (Optional[str]): The name of the experiment.
        description (Optional[str]): The description of the experiment.
        tags (Optional[List[str]]): A list of tags to add to the experiment.
    """

    def __init__(
        self,
        api_key: str,
        project: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        """Initializes an Experiment instance.

        Args:
            api_key (str): The API key for the ExperimentHQ API.
            project (str): The name of the project to log to.
            name (Optional[str]): The name of the experiment.
            description (Optional[str]): The description of the experiment.
            tags (Optional[List[str]]): A list of tags to add to the experiment.
        """
        self.project = project
        self.api_key = api_key
        self.name = name
        self.description = description
        self.tags = tags
        self._session = requests.Session()

        retry_count = 0
        while True:
            try:
                self.experiment_id = self._start_experiment()
                break
            except Exception as e:
                if retry_count > MAX_RETRIES:
                    raise Exception(f"Failed to start experiment due to {e}")

                time.sleep(RETRY_DELAY)
                retry_count += 1

        # Cleanup old experiment before replace it
        previous_experiment = get_global_experiment()
        if previous_experiment is not None and previous_experiment is not self:
            try:
                previous_experiment._on_end()
            except Exception:
                print(
                    f"Failed to clean Experiment: {previous_experiment.experiment_id}",
                )

        set_global_experiment(self)

        self._batch_size = 10
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        # Register the exit handler after starting the thread
        atexit.register(self._exit_handler)

    @property
    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @property
    def _timeout(self) -> int:
        # Send data every 10 seconds
        return 10

    def _exit_handler(self) -> None:
        """Stops the worker thread and waits for it to finish.
        The sentinel task (None) is put into the queue to signal the thread to stop.
        """
        # Put the sentinel task into the queue to tell the thread to stop
        self._update_status("Finished")

        self._queue.put(None)

        # Wait for the worker thread to finish
        self._thread.join()

    def _on_end(self) -> None:
        """Ends the experiment by calling the exit handler when the object is deleted."""
        self._exit_handler()

    def end(self) -> None:
        """Ends the experiment."""
        self._on_end()

    def _update_status(self, status: str) -> None:
        """Updates the status of the experiment.

        Args:
            status (str): The new status for the experiment.
        """
        data = {
            "parameter_name": "Status",
            "parameter_value": status,
            "parameter_type": None,
        }

        response = self._session.post(
            f"{API_URL}experiments/{self.experiment_id}/parameters",
            json=data,
            headers=self._headers,
        )
        if response.status_code != 200:
            # Warn the user that the status was not updated
            print(
                f"Warning: Failed to update experiment status to `{status}`. "
                f"Please update it manually at {NOTION_BASE_URL+self.experiment_id.replace('-', '')}."
            )

    def _worker(self) -> None:
        """Handles the queue of tasks.
        It processes each task, sends batches of data when the batch size is reached, and handles empty queue.
        """
        batch_data = []
        while True:
            try:
                task = self._queue.get(timeout=self._timeout)
            except queue.Empty:
                # If the queue is empty after the timeout, send any remaining data
                if batch_data:
                    self._send_batch(batch_data)
                    batch_data = []
                continue

            if task is None:  # We use None as a sentinel to end the thread.
                # Send any remaining data in the batch before ending the thread.
                if batch_data:
                    self._send_batch(batch_data)
                break
            data = task
            batch_data.append((data))

            # If the batch has reached the desired size, send it.
            if len(batch_data) == self._batch_size:
                self._send_batch(batch_data)
                batch_data = []

    def _send_batch(self, batch_data: List) -> None:
        """Sends a batch of data to the API and handles failures.

        Args:
            batch_data (List): The list of data to be sent.
        """
        try:
            # Send the batch of data to the API
            # remove the retry_count from the data
            post_data = [
                {
                    "parameter_name": data["parameter_name"],
                    "parameter_value": data["parameter_value"],
                    "notion_type": data["parameter_type"],
                }
                for data in batch_data
            ]
            response = self._session.post(
                f"{API_URL}experiments/{self.experiment_id}/parameters",
                json=post_data,
                headers=self._headers,
            )

            if response.status_code not in {200, 401, 400, 404}:
                return self._requeue_failed_tasks(batch_data)
        finally:
            # Mark all tasks in the batch as done.
            for _ in range(len(batch_data)):
                self._queue.task_done()

    def _requeue_failed_tasks(self, failed_tasks: List[Dict]) -> None:
        """Requeues the failed tasks for another try, or prints a warning if retries are exhausted.

        Args:
            failed_tasks (List[Dict]): The list of tasks that failed to send.
        """
        ...
        for task in failed_tasks:
            if task["retry_count"] < MAX_RETRIES:
                task["retry_count"] += 1
                time.sleep(RETRY_DELAY)
                self._queue.put(task)
            else:
                for data in failed_tasks:
                    print(
                        f"Warning: Failed to log parameter `{data['parameter_name']}` with "
                        f"value: `{data['parameter_value']}`. Please add it manually to the "
                        f"corresponding Notion page: ",
                        "{NOTION_BASE_URL+self.experiment_id.replace('-', '')}.",
                    )

    def _start_experiment(self) -> str:
        """Starts the experiment by making a post request to the ExperimentHQ API.

        Returns:
            str: The experiment ID received from the API response.

        Raises:
            Exception: If any error occurred during the request.
        """
        post_data = {
            "project": self.project,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
        }
        response = self._session.post(
            f"{API_URL}experiments",
            json=post_data,
            headers=self._headers,
        )
        if response.status_code == 401:
            raise Exception("Invalid API key.")
        elif response.status_code == 403:
            raise Exception(
                "`Max experiments reached, please upgrade your plan by "
                "reaching out to us at notiontracking@gmail.com`"
            )
        elif response.status_code == 404:
            raise Exception(
                "ExperimentHQ database not found. Please check on ",
                "https://www.experiment-hq.com/account that you connected ",
                "your Notion and also duplicated the ExperimentHQ template.",
            )
        elif response.status_code != 200:
            raise Exception("Failed to start experiment with message: " + response.text)
        elif response.status_code == 408:
            raise Exception("ExperimentHQ API timed out. Experiment not started.")
        return response.json().get("experiment_id")

    def log_parameter(
        self,
        name: str,
        value: Union[
            str,
            int,
            bool,
        ],
        notion_type: Optional[str] = None,
    ) -> None:
        """Logs a parameter to Notion.

        Args:
            name (str): The name of the parameter.
            value (Union[str, int, bool]): The value of the parameter. Depending on the type of the parameter,
                there needs to be a specific format. Please pass several values for multi_select parameters as one
                string separated by commas. The date needs to be in ISO #8601 format and the people parameter needs
                to be a Notion ID.
            notion_type (Optional[str]): Used to create a new column in the Notion database. Setting `notion_type`
                is optional and will be ignored if the column already exists. If the column should be created with
                a specific type, the following types are supported: rich_text, number, select, multi_select, files,
                checkbox, url, email, phone_number, people, date.
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
            "retry_count": 0,
        }

        # Enqueue the task instead of executing it immediately
        self._queue.put(data)
