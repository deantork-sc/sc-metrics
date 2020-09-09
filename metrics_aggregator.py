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

    def print_lead_time(self, project, limit):
        lead_times = self.github.get_lead_time_array(project, limit)
        delta_list = list(map(lambda lead_time: lead_time["delta"], lead_times))
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

    def print_deployment_frequency(self, max_age):
        # TODO update to releases/dev/day
        # TODO see how frequent deployments are on other repos (i.e. mob-api)
        releases_response = self.github.get_releases(project="mob-api")
        releases = json.loads(releases_response.text)
        oldest_release_age = (datetime.datetime.utcnow() -
                              self.github.format_time(releases[-1]["published_at"])).days
        deployment_freq = round(oldest_release_age / len(releases), 2)
        print(f"In the last {max_age} days, got {len(releases)} minor releases. We release, on average, every",
              f"{deployment_freq} days.")

    def print_change_fail(self, max_age):
        # TODO change to all releases, not just minor
        # TODO instead of passing max_age to releases_since, pass the age of the oldest bug (to ensure that out-of-date
        #   bugs aren't being included
        # TODO fetch more releases if some bugs are older than the oldest retrieved release
        utcnow = datetime.datetime.utcnow()
        minor_releases = self.github.get_releases_since(self.github.get_minor_releases(), max_age)
        oldest_release_age = (utcnow - self.github.format_time(minor_releases[-1]["published_at"])).days
        # this query returns tickets created since the oldest considered release that are tagged as bug/support
        # with priority Highest/High
        jql_query = "(project = Silvercar) AND (type = Support OR type = Bug) AND " + \
            f"(priority = Highest OR priority = High) AND created > -{oldest_release_age}d order by createdDate DESC"
        bugs_response = self.jira.search_issue(jql_query=jql_query)
        bugs_count = len(json.loads(bugs_response.text))
        print(f"Got {len(minor_releases)} releases and {bugs_count} bugs since the oldest release",
              f"on {minor_releases[-1]['published_at']}, which is {oldest_release_age} days old.")
        print(f"  Change fail percentage (avg bugs/release) = {round(bugs_count / len(minor_releases), 3)}")


def main():
    metrics = MetricsAggregator()
    # metrics.print_deployment_frequency(max_age=182)
    # metrics.print_change_fail(max_age=182)
    metrics.print_lead_time(project="mob-api", limit=50)


if __name__ == '__main__':
    main()
