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

    # Get the difference between two datetime strings from CircleCI in hours
    def time_delta(self, start_datetime, end_datetime):
        format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
        start_datetime_obj = datetime.datetime.strptime(start_datetime, format_string)
        end_datetime_obj = datetime.datetime.strptime(end_datetime, format_string)
        delta = end_datetime_obj - start_datetime_obj
        # hours not stored in delta object - need to derive from seconds
        return delta.seconds/3600
    
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
                recovery_time_sum += time_delta(build["start_time"], fail_datetime)
        mttr = recovery_time_sum / recovery_count
        return mttr

Circleci = CircleciApi()
response = Circleci.get_builds()
print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))