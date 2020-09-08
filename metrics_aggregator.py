from github_api import GithubApi
from circleci_api import CircleciApi
from jira_api import JiraApi
import datetime
import json


class MetricsAggregator:
    def __init__(self):
        self.github = GithubApi()
        self.circleci = CircleciApi()
        self.jira = JiraApi()

    def timediff_hours(self, start_datetime_obj, end_datetime_obj):
        delta = end_datetime_obj - start_datetime_obj
        # hours not stored in delta object - need to derive from days and seconds
        return delta.days * 24 + delta.seconds / 3600

    def print_lead_time(self, project, limit):
        delta_list = self.github.get_lead_time_array(project, limit)
        count = len(delta_list)
        if count == 0:
            print("No PRs found with current criteria.")
            return
        delta_list.sort()
        average = round(sum(delta_list) / count, 2)
        median = round(delta_list[int(count / 2)], 2)
        print(f"Lead time metrics (in hours) for the last {count} feature PRs in {project}: ")
        print(f"  Median: {median}")
        print(f"  Average: {average}")

    def get_major_releases_since(self, major_releases, age):
        release_count = 0
        utcnow = datetime.datetime.utcnow()
        for release in major_releases:
            time_since_release = utcnow - self.github.format_time(release["published_at"])
            if time_since_release.days > age:
                return major_releases[:release_count]
            release_count += 1
        return major_releases

    def print_deployment_frequency(self, max_age):
        major_releases = self.get_major_releases_since(self.github.get_major_releases(), max_age)
        oldest_release_age = (datetime.datetime.utcnow() - self.github.format_time(major_releases[-1]["published_at"])).days
        deployment_freq = round(oldest_release_age / len(major_releases), 2)
        print(f"In the last {max_age} days, got {len(major_releases)} major releases. We release, on average, every",
              f"{deployment_freq} days.")

    def print_change_fail(self, max_age):
        utcnow = datetime.datetime.utcnow()
        major_releases = self.get_major_releases_since(self.github.get_major_releases(), max_age)
        oldest_release_age = (utcnow - self.github.format_time(major_releases[-1]["published_at"])).days
        # this query returns tickets created since the oldest considered release that are tagged as bug/support
        # with priority Highest/High
        jql_query = "(project = Silvercar) AND (type = Support OR type = Bug) AND " + \
            f"(priority = Highest OR priority = High) AND created > -{oldest_release_age}d order by createdDate DESC"
        bugs_response = self.jira.search_issue(jql_query=jql_query)
        bugs_count = len(json.loads(bugs_response.text))
        print(f"Got {len(major_releases)} releases and {bugs_count} bugs since the oldest release",
              f"on {major_releases[-1]['published_at']}, which is {oldest_release_age} days old.")
        print(f"  Change fail percentage (bugs/releases) = {bugs_count / len(major_releases)}")

    def get_bugs_per_build(self, deployments, bugs, utcnow):
        """
            create an array (bugs_per_build) where each index = bugs that occurred during that build index
            i.e., build 0 is the first build (most recent successful one) we get back. 
            bugs_per_build[0] will be the number of bugs since the most recent build
            bugs_per_build[1] will be the number of bugs between build 1 (second most recent) and build 0
            etc.
        """
        # want to refactor to just get the number of builds we care about, then do bug_count / builds
        deployment_count = len(deployments)
        bug_count = len(bugs)
        bugs_per_build = []
        build_index = 0
        bug_index = 0
        while (bug_index < bug_count) and (build_index < deployment_count):
            # for each bug:
            #   if bug age is less than current build, increment
            #   else, keep incrementing build_index until 
            bug_datetime = self.jira.format_time(bugs[bug_index]["stop_time"])
            bug_age = self.timediff_hours(bug_datetime, utcnow)
            if bug_age < deployments[build_index]["age"]:
                bugs_per_build[bug_index] += 1
                bug_index += 1
            else:
                build_index += 1
        return


def main():
    metrics = MetricsAggregator()
    metrics.print_deployment_frequency(max_age=182)


if __name__ == '__main__':
    main()
