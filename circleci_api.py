import requests
from requests.auth import HTTPBasicAuth
import json
import datetime

class CircleciApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            api_token = data["CIRCLECI_API"]
        self.headers = { 
            "Accept": "application/json",
            "Circle-Token": api_token }

    def format_time(self, datetime_str):
        format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.datetime.strptime(datetime_str, format_string)
    
    def get_builds(self, project, limit, filter=None):
        if (filter):
            filter = f"&filter={filter}"
        else:
            filter = ""
        url = f"https://circleci.com/api/v1.1/project/github/silvercar/{project}?limit={limit}{filter}&shallow=true"
        return requests.request( "GET", url, headers=self.headers)

    def get_deployments(self):
        # filter to only build-publish builds or something


    def get_mttr(self, project):
        response = get_builds(15, project)
        build_array = json.loads(response.text)
        build_array.reverse()
        recovery_time_sum = 0
        recovery_count = 0
        found_failed = False
        fail_datetime = ""
        for build in build_array:
            if (build["outcome"] == "failed"):
                found_failed = True
                fail_datetime = build["stop_time"]
            if (build["outcome"] == "success" and found_failed):
                found_failed = False
                recovery_count += 1
                recovery_time_sum += time_delta(build["start_time"], fail_datetime)
        mttr = recovery_time_sum / recovery_count
        return mttr

    def get_workflows(self):
        url = 'https://circleci.com/api/v2/insights/github/silvercar/dw-web/workflows?limit=15&branch=master'
        return requests.request( "GET", url, headers=self.headers)

    def demo(self):
        builds = self.get_builds(limit=5, project="dw-web").text
        with open('builds.json', 'w') as outfile:
            json.dump(json.loads(builds), outfile)

        workflows = self.get_workflows().text
        with open('workflows.json', 'w') as outfile:
            json.dump(json.loads(workflows), outfile)

circleci = CircleciApi()
builds_resp = circleci.get_builds("mob-api", 1, "successful")
print(json.dumps(json.loads(builds_resp.text), sort_keys=True, indent=4, separators=(",", ": ")))
print(datetime.datetime.utcnow())
