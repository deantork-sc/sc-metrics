import requests
from requests.auth import HTTPBasicAuth
import json
import datetime

class GithubApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            token = data["GITHUB_PAT"]
        self.debug = False
        self.headers = { 
            "Accept": "Accept: application/vnd.github.v3+json",
            "Authorization": f"token {token}" }
    
    def time_delta(self, start_datetime, end_datetime):
        format_string = "%Y-%m-%dT%H:%M:%SZ"
        start_datetime_obj = datetime.datetime.strptime(start_datetime, format_string)
        end_datetime_obj = datetime.datetime.strptime(end_datetime, format_string)
        delta = end_datetime_obj - start_datetime_obj
        # hours not stored in delta object - need to derive from days and seconds
        return delta.days * 24 + delta.seconds/3600

    def get_prs(self, project, state, limit):
        if (limit > 100):
            print("PRs limited to 100 per page - if you want to use more, need to paginate")
        url = f"https://api.github.com/repos/silvercar/{project}/pulls?state={state}&per_page={limit}"
        return requests.request( "GET", url, headers=self.headers)

    def get_lead_time_array(self, project, limit):
        prs_json = json.loads(self.get_prs(project, "closed", limit).text)
        delta_list = []
        bugfix_count = 0
        release_count = 0
        other_count = 0
        unlabeled_count = 0
        for pr in prs_json:
            pr["body"] = pr["body"][:80].replace("[X]", "[x]")
            if (self.debug):
                print(pr["title"])
                print("  Body: " + repr(pr["body"][:80]) + "...")
            if ("[x] Feature" not in pr["body"]):
                if "[x] Bug Fix" in pr["body"]:
                    bugfix_count += 1
                if "[x] Release" in pr["body"]:
                    release_count += 1
                if "[x] Other" in pr["body"]:
                    other_count += 1
                if ("[x]" not in (pr["body"][:80])):
                    if ("bump version" in pr["title"]) or ("Bump version" in pr["title"]):
                        release_count += 1
                    else:
                        unlabeled_count += 1
                        if (self.debug):
                            print("unlabeled")
                continue
            commits_response = requests.request("GET", url=pr["commits_url"], headers=self.headers)
            commits_json = json.loads(commits_response.text)
            # commits_json is an array of commit objects, from oldest as first elem to most recent as last elem
            start_datetime = commits_json[0]["commit"]["committer"]["date"]
            end_datetime = commits_json[-1]["commit"]["committer"]["date"]
            if (self.debug):
                print(f"  start={start_datetime}, end={end_datetime}")
            delta = self.time_delta(start_datetime, end_datetime)
            if (len(commits_json) > 0):
                # don't want to factor in single-commit PRs, as they have lead time of 0
                delta_list.append(delta)
        print(f"  In the last {limit} PRs, found {len(delta_list)} features, {bugfix_count} bugfixes, {release_count} releases, {unlabeled_count} unlabeled, and {other_count} misc. others.")
        return delta_list
