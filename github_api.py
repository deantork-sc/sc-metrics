import requests
import json
import datetime


class GithubApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            token = data["GITHUB_PAT"]
        self.debug = True
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "Accept: application/vnd.github.v3+json",
            "Authorization": f"token {token}"}

    def format_time(self, datetime_str):
        format_string = "%Y-%m-%dT%H:%M:%SZ"
        return datetime.datetime.strptime(datetime_str, format_string)

    def is_event_older_than_other(self, event, other):
        event_datetime = self.format_time(event)
        older_than_datetime = self.format_time(other)
        # if event is older than older_than, then older_than - event is positive
        return (older_than_datetime - event_datetime) > datetime.timedelta(0)

    def time_diff_hours(self, lhs_datetime_str, rhs_datetime_str):
        lhs_datetime = self.format_time(lhs_datetime_str)
        rhs_datetime = self.format_time(rhs_datetime_str)
        delta = (lhs_datetime - rhs_datetime)
        # timedelta does not store hours, need to compute manually
        return delta.total_seconds() / 3600

    def sort_prs(self, prs):
        # sorts PRs in descending order (newest to oldest)
        sorted(prs, key=lambda pr: self.format_time(pr["merged_at"]), reverse=True)

    def get_prs(self, project, state, limit, page=0):
        if limit > 100:
            print("PRs limited to 100 per page - if you want to use more, need to paginate")
        url = f"{self.base_url}/repos/silvercar/{project}/pulls?state={state}&per_page={limit}&page={page}"
        return requests.request("GET", url, headers=self.headers)

    def is_feature_pr(self, pr):
        pr["body"] = pr["body"][:80].replace("[X]", "[x]")
        if "[x] Feature" in pr["body"]:
            return True
        return False

    def get_feature_prs(self, project, limit, page=0):
        prs = json.loads(self.get_prs(project=project, limit=limit, page=page, state="closed").text)
        return list(filter(self.is_feature_pr, prs))

    def add_start_time(self, prs):
        for pr in prs:
            commits_response = requests.request("GET", url=pr["commits_url"], headers=self.headers)
            commits_json = json.loads(commits_response.text)
            # commits_json is an array of commit objects, from oldest as first elem to most recent as last elem
            pr["start_time"] = commits_json[0]["commit"]["committer"]["date"]

    def get_releases(self, project, page=0):
        url = f"{self.base_url}/repos/silvercar/{project}/releases?base=master&page={page}"
        return requests.request("GET", url, headers=self.headers)

    def get_minor_releases(self):
        releases_response = self.get_releases("dw-web")
        releases = json.loads(releases_response.text)
        return list(filter(lambda release: release["tag_name"].split('.')[2] == '0', releases))

    def get_recent_pr_statistics(self, project, limit):
        feature_count = 0
        bugfix_count = 0
        release_count = 0
        other_count = 0
        unlabeled_count = 0
        prs = json.loads(self.get_prs(project, "closed", limit).text)
        for pr in prs:
            pr["body"] = pr["body"][:80].replace("[X]", "[x]")
            if self.debug:
                print(pr["title"])
                print("  Body: " + repr(pr["body"][:80]) + "...")
            if "[x] Feature" in pr["body"]:
                feature_count += 1
            if "[x] Bug Fix" in pr["body"]:
                bugfix_count += 1
            if "[x] Release" in pr["body"]:
                release_count += 1
            if "[x]" in (pr["body"][:80]):
                # _something_ is checked, just don't know what
                other_count += 1
            else:
                if ("bump version" in pr["title"]) or ("Bump version" in pr["title"]):
                    release_count += 1
                else:
                    unlabeled_count += 1
                    if self.debug:
                        print("unlabeled")
                continue
        print(f"  In the last {limit} PRs, found {feature_count} features, {bugfix_count} bugfixes, {release_count}",
              f"releases, {unlabeled_count} unlabeled, and {other_count} misc. others.")

    def get_lead_time_array(self, project, limit):
        prs = self.get_feature_prs(project=project, limit=limit)
        self.sort_prs(prs)
        self.add_start_time(prs)
        releases = json.loads(self.get_releases(project=project).text)
        lead_times = []
        release_index = 0
        pr_index = 0
        # while most recent release date is older than the current PR, go to next PR
        # do this because we only want to look at released PRs
        while self.is_event_older_than_other(event=releases[release_index]["published_at"],
                                             other=prs[pr_index]["merged_at"]):
            if pr_index == len(prs):
                raise RuntimeError("No released PRs within limit")
            if self.debug:
                print("Current diff in initial ff:",
                      self.time_diff_hours(prs[0]["merged_at"], releases[release_index]["published_at"]))
            pr_index += 1
        while pr_index < len(prs):
            if release_index == len(releases):
                raise RuntimeError("Need more releases")
            current_delta = self.time_diff_hours(releases[release_index]["published_at"], prs[pr_index]["start_time"])
            if self.debug:
                print(f"First commit on pr: {prs[pr_index]['start_time']}.\n"
                      f"Current release:    {releases[release_index]['published_at']}\n"
                      f"Hours between work started and release: {current_delta}")

            # if the current PR is older than the next release, go to next release
            # else, find the time discrepancy between this PR and the currently focused release
            if self.is_event_older_than_other(event=prs[pr_index]["merged_at"],
                                              other=releases[release_index + 1]["published_at"]):
                release_index += 1
                print ("Current delta:", current_delta)
            else:
                lead_times.append({
                    "author": prs[pr_index]["user"]["login"],
                    "delta": current_delta
                })
                if self.debug:
                    print(f"Time diff: {current_delta}, author: {prs[pr_index]['user']['login']}")
                pr_index += 1
            print("")
        return lead_times

    def demo(self):
        releases = self.get_releases(project="dw-web").text
        with open('releases.json', 'w') as outfile:
            json.dump(json.loads(releases), outfile)

        prs = self.get_prs(project="mob-api", state="closed", limit=5).text
        with open('prs.json', 'w') as outfile:
            json.dump(json.loads(prs), outfile)


github = GithubApi()
github.demo()
