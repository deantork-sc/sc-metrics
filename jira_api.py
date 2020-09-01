import requests
from requests.auth import HTTPBasicAuth
import json
import datetime

class JiraApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            api_token = data["JIRA_API"]
        self.auth = HTTPBasicAuth("dean.torkelson@silvercar.com", api_token)
        self.headers = { "Accept": "application/json" }

    # Get the difference between two datetime strings from JIRA in hours
    def time_delta(self, start_datetime, end_datetime):
        format_string = "%Y-%m-%dT%H:%M:%S.%f%z"
        start_datetime_obj = datetime.datetime.strptime(start_datetime, format_string)
        end_datetime_obj = datetime.datetime.strptime(end_datetime, format_string)
        delta = end_datetime_obj - start_datetime_obj
        # hours not stored in delta object - need to derive from seconds
        return delta.seconds/3600

    def get_issue_changelog(self, issue_id):
        url = f"https://silvercar.atlassian.net/rest/api/3/issue/{issue_id}/changelog"
        return requests.request( "GET", url, headers=self.headers, auth=self.auth)

    def get_single_issue_leadtime(self, issue_id):
        response = self.get_issue_changelog(issue_id)
        response_json = json.loads(response.text)
        start_datetime = ""
        end_datetime = ""
        for event in response_json["values"]:
            for item in event["items"]:
                # want to select only the first "created" event we see
                if (item["toString"] == "In Progress" and start_datetime == ""):
                    start_datetime = event["created"]
                # as soon as it's resolved, consider it done for good
                if (item["field"] == "resolution" and start_datetime != ""):
                    end_datetime = event["created"]
                    return self.time_delta(start_datetime, end_datetime)
        changelog = json.dumps(response_json, sort_keys=True, indent=4, separators=(",", ": "))
        raise RuntimeError("error: start or end not set. changelog json:\n" + changelog)

    def get_group(self):
        url = f"https://silvercar.atlassian.net/rest/api/3/groupuserpicker?query=dean"
        return requests.request( "GET", url, headers=self.headers, auth=self.auth)

    def search_issue(self):
        # gets helpdesk tasks that have been finished
        jql = "project = HLP AND issuetype = Task AND status = Done AND createdDate > startOfYear()"
        url = f"https://silvercar.atlassian.net/rest/api/3/search?jql={jql}"
        return requests.request( "GET", url, headers=self.headers, auth=self.auth)

    def get_issue(self):
        url = f"https://silvercar.atlassian.net/rest/api/3/issue/HLP-3335"
        return requests.request( "GET", url, headers=self.headers, auth=self.auth)

jira = JiraApi()
response = json.dumps(json.loads(jira.get_issue().text))
print(response)