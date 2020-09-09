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

    def get_prs(self, project, state, limit, page=0):
        # TODO check for 200 status code, handle error resp
        url = f"{self.base_url}/repos/silvercar/{project}/pulls?state={state}&per_page={limit}&page={page}"
        return requests.request("GET", url, headers=self.headers)

    def get_releases(self, project, page=0):
        # TODO check for 200 status code, handle error resp
        url = f"{self.base_url}/repos/silvercar/{project}/releases?base=master&page={page}"
        return requests.request("GET", url, headers=self.headers)

    # Adds the timestamp of the first commit to every PR in a list of PRs
    def add_start_time(self, prs):
        for pr in prs:
            commits_response = requests.request("GET", url=pr["commits_url"], headers=self.headers)
            commits_json = json.loads(commits_response.text)
            # commits_json is an array of commit objects, from oldest as first elem to most recent as last elem
            pr["start_time"] = commits_json[0]["commit"]["committer"]["date"]

    # Creates a datetime object given a GitHub-style datetime string
    def format_time(self, datetime_str):
        format_string = "%Y-%m-%dT%H:%M:%SZ"
        return datetime.datetime.strptime(datetime_str, format_string)

    # Finds the difference, in hours, between two GitHub-style datetime strings
    def time_diff_hours(self, lhs_datetime_str, rhs_datetime_str):
        lhs_datetime = self.format_time(lhs_datetime_str)
        rhs_datetime = self.format_time(rhs_datetime_str)
        delta = (lhs_datetime - rhs_datetime)
        # timedelta does not store hours, need to compute manually
        return delta.total_seconds() / 3600

    # Returns true if `event` is older, or took place before, `other`
    # Both `event` and `other` are assumed to be GitHub-style datetime strings
    def is_event_older_than_other(self, event, other):
        event_datetime = self.format_time(event)
        older_than_datetime = self.format_time(other)
        # if event is older than older_than, then older_than - event is positive
        return (older_than_datetime - event_datetime) > datetime.timedelta(0)

    # Sorts a list of PRs in descending order (newest to oldest), based on merge time
    def sort_prs(self, prs):
        sorted(prs, key=lambda pr: self.format_time(pr["merged_at"]), reverse=True)

    # Returns true if a given PR is marked as a feature, false otherwise
    def is_feature_pr(self, pr):
        return "[x] Feature" in pr["body"][:80].replace("[X]", "[x]")

    # Returns a list of PRs marked as features
    def get_feature_prs(self, project, limit, page=0):
        prs = json.loads(self.get_prs(project=project, limit=limit, page=page, state="closed").text)
        return list(filter(self.is_feature_pr, prs))

    # Returns a list of releases that are marked as either major or minor versions (i.e. no patch versions)
    def get_minor_releases(self):
        releases_response = self.get_releases("dw-web")
        releases = json.loads(releases_response.text)
        return list(filter(lambda release: release["tag_name"].split('.')[2] == '0', releases))

    # Slices a list of releases to only include the releases that are less than `age` days old
    def get_releases_since(self, releases, age):
        release_count = 0
        utcnow = datetime.datetime.utcnow()
        for release in releases:
            time_since_release = utcnow - self.format_time(release["published_at"])
            if time_since_release.days > age:
                return releases[:release_count]
            release_count += 1
        return releases

    # Prints statistics about what the last `limit` PRs have been marked as in the body of the PR
    def print_recent_pr_types(self, project, limit):
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
        print(f"In the last {limit} PRs, found {feature_count} features, {bugfix_count} bugfixes, {release_count}",
              f"releases, {unlabeled_count} unlabeled, and {other_count} misc. others.")

    # Returns a list of dictionary objects that correlate lead time (time from first commit of a ticket to its release)
    # to the GitHub username of the author
    def get_lead_time_array(self, project, limit):
        prs = self.get_feature_prs(project=project, limit=limit)
        self.sort_prs(prs)
        self.add_start_time(prs)
        releases = json.loads(self.get_releases(project=project).text)
        lead_times = []
        release_index = 0
        pr_index = 0
        # this loop skips over PRs that haven't been released yet by comparing the date of the most recent release
        # to the merged date of the current PR
        while self.is_event_older_than_other(event=releases[release_index]["published_at"],
                                             other=prs[pr_index]["merged_at"]):
            if pr_index == len(prs):
                raise RuntimeError("No released PRs within given limit")
            if self.debug:
                print("Current diff in initial ff:",
                      self.time_diff_hours(prs[0]["merged_at"], releases[release_index]["published_at"]))
            pr_index += 1
        # iterate over every PR and find its lead time
        while pr_index < len(prs):
            if release_index == len(releases):
                raise RuntimeError("Need to fetch more releases")

            lead_time = self.time_diff_hours(releases[release_index]["published_at"], prs[pr_index]["start_time"])
            if self.debug:
                print(f"First commit on pr: {prs[pr_index]['start_time']}.\n"
                      f"Current release:    {releases[release_index]['published_at']}\n"
                      f"Hours between work started and release: {lead_time}")

            # if the current PR was merged before the previous release, increment to that release
            # else, find the time discrepancy between this PR and the current release
            if self.is_event_older_than_other(event=prs[pr_index]["merged_at"],
                                              other=releases[release_index + 1]["published_at"]):
                release_index += 1
                print("Current delta:", lead_time)
            else:
                lead_times.append({
                    "author": prs[pr_index]["user"]["login"],
                    "delta": lead_time
                })
                if self.debug:
                    print(f"Time diff: {lead_time}, author: {prs[pr_index]['user']['login']}")
                pr_index += 1
            if self.debug:
                print()
        return lead_times

    # Demonstrates example JSON response data
    def demo(self):
        releases = self.get_releases(project="dw-web").text
        with open('releases.json', 'w') as outfile:
            json.dump(json.loads(releases), outfile)

        prs = self.get_prs(project="mob-api", state="closed", limit=5).text
        with open('prs.json', 'w') as outfile:
            json.dump(json.loads(prs), outfile)


github = GithubApi()
github.demo()
