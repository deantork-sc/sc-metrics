import requests
import json
import datetime


class CircleciApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            api_token = data["CIRCLECI_API"]
        self.base_url = "https://circleci.com/api"
        self.headers = {
            "Accept": "application/json",
            "Circle-Token": api_token}

    def format_time(self, datetime_str):
        format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.datetime.strptime(datetime_str, format_string)

    def get_builds(self, project, limit, filter=None):
        if filter:
            filter = f"&filter={filter}"
        else:
            filter = ""
        url = f"{self.base_url}/v1.1/project/github/silvercar/{project}?limit={limit}{filter}&shallow=true"
        return requests.request("GET", url, headers=self.headers)

    def get_workflows(self, project):
        url = f"{self.base_url}/v2/insights/github/silvercar/{project}/workflows"
        return requests.request("GET", url, headers=self.headers)

    def demo(self):
        builds = self.get_builds(limit=10, project="mob-api").text
        with open('builds.json', 'w') as outfile:
            json.dump(json.loads(builds), outfile)

        workflows = self.get_workflows(project="mob-api").text
        with open('workflows.json', 'w') as outfile:
            json.dump(json.loads(workflows), outfile)
