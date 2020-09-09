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
#### Formula
Calculated as the average amount of time between the first commit of a feature PR and the next release after the PR is merged, for all feature PRs out of the last however many closed PRs total

## MTTR
#### Goal
Get the percentage of the time we experience a service outage
#### Formula
TBD

## Deployment frequency
#### Goal
Get the average number of releases per developer, per day
#### Formula
Currently calculated as the average number of releases, per day, for a given repo
#### Potential bugs
Not all repos create releases

## Change fail percentage
#### Goal
Find the number of Highest/High priority bugs between the previous build and the current build, per build
#### Formula
Currently calculated as the average number of bugs fitting the above criteria per each minor release 

