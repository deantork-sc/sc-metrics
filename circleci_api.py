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

    def get_deployments(self, builds, project, limit):
        if (project == "mob-api"):
            deployment_title = "build"
            # need to also check for deploy-prd step
        elif (project == "dw-web"):
            deployment_title = "build-publish"
        # only return builds whose workflow is a successful deployment
        return filter(lambda build: build["workflows"]["workflow-name"] == deployment_title, builds)
                
    # currently out of date: will likely be getting this data from AWS/CloudWatch
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

    def get_workflows(self, project):
        url = f'https://circleci.com/api/v2/insights/github/silvercar/{project}/workflows'
        return requests.request( "GET", url, headers=self.headers)

    def demo(self):
        builds = self.get_builds(limit=10, project="mob-api").text
        with open('builds.json', 'w') as outfile:
            json.dump(json.loads(builds), outfile)

        workflows = self.get_workflows(project="mob-api").text
        with open('workflows.json', 'w') as outfile:
            json.dump(json.loads(workflows), outfile)

circleci = CircleciApi()
circleci.demo()
