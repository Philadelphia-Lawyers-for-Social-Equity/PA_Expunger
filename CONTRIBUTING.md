# Guidelines for contributing

## Overview

This document will outline guidelines for contributing to the docket-dashboard [codebase](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard).

## A note about sensitivity

This project is built to help the lawyers at Philadelphia Lawyers for Social Equity (PLSE) to more efficiently help their clients, people whose lives will be made easier by expunging their criminal records. While most of the data we use has been anonymized, occasionally we will see real people's records and should treat that with sensitivity.

It is vital to this project that the developers building this value the privacy, dignity, and wellbeing of the people we are trying to help. All writing, code, and communication should reflect this.

## Joining the regular meetings

We host biweekly meetings both in person and remotely. This is largely where we make decisions, communicate PLSE's needs, and set up collaborative pairing sessions to get large chunks of work done.

The best way to find out about our meetings is joining the [#plse-expungement](https://app.slack.com/client/T03NV85SZ/CJDHS591S) channel on the [Code for Philly](https://www.codeforphilly.org/) [Slack](https://www.codeforphilly.org/chat/).

## Issues

While most of our issues are created by the team lead from requests by the lawyers at PLSE, occasionally we identify needs that we can write up individually.

We also use issues for tracking our own team needs (e.g. adding documentation).

### Add an issue

Navigate to our [issues page on Github](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/issues) and hit the big green `New` button.

### Types of issues

There are two types of issues we currently use: `Bug Reports` and `Feature Requests`. There are templates for each and following those templates is a great way to make sure we are providing enough context for other developers as we write issues. 

#### Bug reports

Bug Reports are for reporting bugs in the code.

Most of the issues contributors submit will be bug reports since contributors often poke at the app and use tools like the console and inspector while using the app. Bug Reports need to properly provide context for the environment and conditions the bug us being seen under.

Good instructions for recreation are key to speedy development of fixes.

#### Feature requests

Feature Requests are for asking for new parts of the app, e.g. a notification system.

Most of our feature requests will come from the lawyers at PLSE, but occasionally contributors will find something in need of improvement or new needed for the app.

Clear context of why this new feature is needed and clear descriptions of what is wanted are key to developing new features.

## Making code changes

Changes to our codebase should always address an [issue](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/issues) and need to be requested to be merged by submitting a pull request that will be reviewed by at least the team lead or two other contributors.

### Choose an issue

Look through the [issues page](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/issues) in the repo.

Find a task that has no current assignees and sounds like a task that either you can confidently take on yourself or involves a new language, framework, or design that you want learn.

For the latter it is best to pair on this with a team member experienced with that thing you want to learn. 

### Create a branch for your work

Our default branch to work from is `develop`. To create a new branch for your work:

```sh
# In the docket-dashboard root, go to develop
git checkout develop

# Pull down the most recent commits
git pull

# Make a new branch
git branch <new-branch-name>
git checkout <new-branch-name>

# Or for a one liner (-b creates a new branch when checking out)
git checkout -b <new-branch-name>
```

Branch names should be in kebab case (all lower case, dashes separate words) and are best when short and descriptive.

### Commit your work

Any good work with code involves good commit messages.

The best commit messages read like instructions on how to recreate the code being committed.

Individual commits should be small chunks of work included together as one step in the process.

### Push your work up to the remote repo

When you have completed your work and made good commit messages that read like clear instructions, you will want to push your work up to our remote repository on Github.

```sh
# Make a matching remote branch to push to
# Note: While it is usually `origin`, the remote repo may be named a different alias on your machine
git push --set-upstream origin <new-branch-name>

# Once you have set up a remote branch continue to push changes with:
git push
```

### Create a pull request

In order to merge your work to the `develop` branch you must create a pull request.

Often Github will put up a notification that a new branch has been pushed and give a green "Make a PR" button on any page of the repo. If you don't see this you can go to the [pull requests tab](https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/pulls) and hit the big green `New` button.

There is a template to follow to make sure that reviewers have enough context about the changes you made and what they fix.

It is vital to provide clear instructions how to test the changes you made.

Please also make sure you tag the issue you are addressing. You can do this when writing the PR by writing `#<number>` in the `Does this close any currently open issues` section.

```md
<!-- For example, for a PR addressing issue #13 -->
Closes #13
```

To make sure reviewers know to review it, finish up by assigning either the team lead or two team members in the 'reviewers' tab in the sidebar or under the PR text depending on your view.

### Reviewed work

The reviewer(s) will either ask for changes or approve the PR.

If changes are requested, please make the changes in your branch and push them up to Github when ready.

```bash
# Tip: If you are fixing something from a particular commit, you can create a !fixup commit with
git commit --fixup <sha-for-commit>

# Then, when approved, before you merge you can use:
git rebase -i --autosquash develop
# to squash your !fixup commits into their corresponding commits
```

Once you have pushed up your fixes, let your reviewer know and they will follow up and look again. This may loop a few times.

Once your changes are approved, you can hit the `merge` button to merge to the `develop` branch (unless specified otherwise).

Please also delete the branch from Github (you'll be prompted).

### Clean up

Once you've merged your work go back to your terminal

```sh
# Go to the develop branch
git checkout develop

# Pull down the changes you merged
git pull

# Delete the branch from your local machine
git branch -d <new-branch-name>
```
