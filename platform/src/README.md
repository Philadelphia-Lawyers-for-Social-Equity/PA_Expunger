# Expungement Platform

This Django project provides expungement paperwork and record access to the
PLSE lawyers and volunteers.

## Status
- Initializes user groups
- Initializes superuser

## Setup / Running

One current goal is to bypass these steps.  We'd like to have
expunger-infrastructure handle setup and running.  Not there yet.

Current process:

- Start the expungement-infrastructure via docker-compose
- From expungement-infrastructere, load the environmental variables:
    `$ source local_envs.sh`

**First time?**
- You *may* need to install the system libraries from requirements.debian.txt.
- Install python libraries
  **in a [virtual environment](https://github.com/sashahart/vex).**
        `$ pip install -r requirements.txt`
- Run `$ ./manage.py makemigrations`

Continuing after first time setup:
- Run a local server. `$ ./manage.py runserver`
- Visit `http://localhost:8000` with the username and password from
  local_envs.sh if you want to poke around.
