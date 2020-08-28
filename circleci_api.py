import requests
from requests.auth import HTTPBasicAuth
import json
import datetime

class CircleciApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            api_token = data["CIRCLECI_API"]
        self.headers = { "Circle-Token": api_token }

    # goal: find diff between any "failed" and the next "success"
    def get_builds(self, limit, project):
        url = f"https://circleci.com/api/v1.1/project/github/{project}/mob-api?limit={limit}&shallow=true"
        return requests.request( "GET", url, headers=self.headers)

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
                recovery_time_sum += timedelta(build["queued_at"], fail_datetime)
        mttr = recovery_time_sum / recovery_count
        return mttr

Circleci = CircleciApi()
response = Circleci.get_builds()
print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))