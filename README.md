# sc-metrics overview
Please note that this document is very volatile and may not be up to date with latest project reqs

## Goal metrics:
* Lead time
* MTTR
* Deployment frequency
* Change fail percentage

## Sources:
* [JIRA](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
* [GitHub](https://docs.github.com/en/rest)
* [CircleCI](https://circleci.com/docs/api/#projects)
* AWS (for MTTR)

### Misc.
Base it off of Accelerate Four Key Metrics
Want to group by scrum team and individual

# Working notes

## Lead time
#### Goal
Get the time it takes between start of work on a story and that story's deployment to the code
#### Ideas
If all tickets are closed as soon as they are merged into master, just get time discrepancy between when issue was opened and when it was closed
#### Programatic solution
* [Get all issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get) for a team in a given timespan
* Filter the issues to only see the closed issues
* Look at each [issue's changelog](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-changelog-get) to get time of assignment and time that status was set to done
* Find the difference between the two 
* Find the average of these differences for a team/individual
#### Potential bugs
* Timezones
* Do all teams have the same workflow with how they handle ticket statuses?
    temporary fix: don't check for "done", check for "resolution"

## MTTR
#### Goal
Get the percentage of the time we experience a service outage
#### Ideas
#### Programatic solution

## Deployment frequency
#### Goal
Get the average number of releases per developer, per day
#### Ideas
#### Programatic solution

## Change fail percentage
#### Goal
Find the percentage of master builds that fail
#### Ideas
For some number of builds on master, find what percentage failed compared to the percentage that succeeded
#### Programatic solution
* Get [some number of builds](https://circleci.com/docs/api/#recent-builds-for-a-single-project) (30? 100?) for the project
* Filter these results to only be builds on master that either succeeded or failed
* Calculate the ratio of failed builds to total
