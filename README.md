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
If all tickets are closed as soon as they are merged into master, just get time discrepancy between first and last commit
#### Programatic solution
* From GitHub, get the last 100 successful PRs in some repo (mob-api? dw-web?)
* Get the diff between the timestamp of the first commit and the timestamp of when the PR was merged
* From the description, scrape the story title (optional, for debugging)
#### Potential bugs

## MTTR
#### Goal
Get the percentage of the time we experience a service outage
#### Ideas
See conversation with Anthony
#### Programatic solution

## Deployment frequency
#### Goal
Get the average number of releases per developer, per day
#### Ideas
Does CircleCI provide enough correct information? AWS?
#### Programatic solution

## Change fail percentage
#### Goal
Find the number of Highest/High priority bugs (type = bug/support) between the previous build and the current build, per build
#### Ideas
see above
#### Programatic solution
* Get list of bugs from JIRA
* Get list of successful builds from CircleCI
* For each bug, find which build it occurred in
* Get the average of bugs per build

