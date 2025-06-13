# Guidelines for contributing

## Overview

This document will outline guidelines for contributing to the PA Expunger [codebase](https://github.com/Philadelphia-Lawyers-for-Social-Equity/PA_Expunger).

## A note about sensitivity

This project is built to help the lawyers at Philadelphia Lawyers for Social Equity (PLSE) to more efficiently help their clients, people whose lives will be made easier by expunging their criminal records. While most of the data we use has been anonymized, occasionally we will see real people's records and should treat that with sensitivity.

It is vital to this project that the developers building this value the privacy, dignity, and wellbeing of the people we are trying to help. All writing, code, and communication should reflect this.

## Joining the regular meetings

We host two meetings per month, one at the Code for Philly hacknight, and one remotely. This is largely where we make decisions, communicate PLSE's needs, and set up collaborative pairing sessions to get large chunks of work done.

The best way to find out about our meetings is joining the [#pax](https://app.slack.com/client/T03NV85SZ/CJDHS591S) channel on the [Code for Philly](https://www.codeforphilly.org/) [Slack](https://www.codeforphilly.org/chat/).

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

## Managing Frontend Dependencies

Our frontend is built using **Yarn v4** with the **Zero-Installs**. This provides a reliable and consistent development environment for everyone.

### Key Concepts

* **Zero-Installs:** Instead of a `node_modules` folder, all package dependencies are stored as zip archives inside the `.yarn/cache` directory.
* **Plug'n'Play (PnP):** A file named `.pnp.cjs` tells Node.js how to find and load these packages directly from the cache.
* **Checked-in Dependencies:** Because of this setup, the `.yarn/cache` directory and the `.pnp.cjs` file are checked directly into Git. This means you don't need to run `yarn install` after cloning the repository—all dependencies are already there.

### The Golden Rule

> **IMPORTANT:** To ensure consistency across all operating systems, any command that modifies dependencies (`yarn add`, `yarn remove`, `yarn up`) **must be run inside a specific Docker container**, not on your host machine (e.g., your Mac or Windows laptop).
>
> Running these commands locally can write platform-specific binaries to the cache, which will break the build for other developers or in CI/CD environments.

### The Correct Workflow for Updating Dependencies

Follow these steps precisely whenever you need to add, update, or remove a frontend package.

**1. Run the Dependency Management Container**

From the root of the project, run the following command. This starts a temporary, clean Node.js container and mounts your project directory into it.

```bash
# On macOS, Linux, or Windows with Git Bash:
cd frontend/src # location of package.json
docker run -it --rm -v "${PWD}:/app" -w /app node:20-alpine sh -c "corepack enable && sh"

# On Windows with Command Prompt (CMD):
cd frontend/src
docker run -it --rm -v "%CD%:/app" -w /app node:20-alpine sh -c "corepack enable && sh"
```

**Understanding the Command:**

* `docker run`: Executes a command in a new container.
* `-it`: Keeps the session interactive, so you can type commands.
* `--rm`: Automatically removes the container when you exit, keeping your system clean.
* `-v "${PWD}:/app"`: Mounts your current project directory (represented by `${PWD}`) into the `/app` directory inside the container.
* `-w /app`: Sets the working directory inside the container to `/app`.
* `node:20-alpine`: Specifies the image to use, which is the same as our frontend's base image.
* `sh -c "corepack enable && sh"`: A command that first enables `corepack` (Yarn's modern manager) and then starts an interactive shell (`sh`) for you to use.

**2. Modify Dependencies**

Once you are inside the container's shell (your terminal prompt will change), you can run your Yarn commands as usual.

**To add a new package:**

```sh
yarn add <package-name>
```

**To see latest versions of packages and upgrade them:**

```sh
yarn upgrade-interactive
```

**To remove a package:**

```sh
yarn remove <package-name>
```

**3. Exit the Container**

When you are finished, simply type `exit` and press Enter to close the container.

```sh
exit
```

**4. Commit Your Changes**

After exiting the container, you will see that files in your local project directory have been modified. You must commit all of these changes to your pull request. This typically includes:

* `package.json`
* `yarn.lock`
* `.pnp.cjs`
* `.pnp.loader.mjs`
* New or updated files within the `.yarn/cache` directory.

By following this process, you ensure that the dependency cache remains consistent and platform-agnostic for the entire team.
