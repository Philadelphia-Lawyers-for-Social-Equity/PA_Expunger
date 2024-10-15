FROM python:3.12

ENV INSTALL_DIR /srv/plse/install
ENV APP_DIR /srv/plse/expunger

ARG EXPUNGER_USER
ARG EXPUNGER_PASS
ARG EXPUNGER_KEY
ARG DJANGO_SETTINGS_MODULE
ARG REACT_APP_BACKEND_HOST
ARG BACKEND_ONLY

ENV PATH "$PATH:/home/${EXPUNGER_USER}/.local/bin"

# System initialization

WORKDIR $INSTALL_DIR
RUN apt-get update -y -qq && \
    apt-get upgrade -y -qq && \
    apt-get install -y -qq \
    apache2 \
    apache2-dev \
    build-essential \
    git \
    pkg-config \
    libcurl4-openssl-dev \
    libpoppler-cpp-dev \
    libssl-dev \
    tzdata \
    libffi-dev \
    libpq-dev \
    vim \
    # Cleanup
    && apt-get autoremove -y \
    && apt-get purge -y \
    && apt-get clean -y

# TODO: see below about adding this to production build only
# https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/issues/47
# Install Yarn for production frontend build later
RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - && \
    apt-get install -y -qq nodejs
RUN npm install -g yarn

# timezone-related fixes
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Provide a local user environment
# https://jtreminio.com/blog/running-docker-containers-as-current-host-user/#ok-so-what-actually-works
ARG USER_ID
ARG GROUP_ID

RUN if [ ${USER_ID:-0} -ne 0 ] && [ ${GROUP_ID:-0} -ne 0 ];\
    then \
        if getent group ${EXPUNGER_USER}; then groupdel ${EXPUNGER_USER}; fi; \
        if getent passwd ${EXPUNGER_USER}; then userdel -f ${EXPUNGER_USER}; fi; \
        groupadd -g ${GROUP_ID} ${EXPUNGER_USER} && \
        useradd -m -l -u ${USER_ID} -g ${EXPUNGER_USER} ${EXPUNGER_USER} \
    ; else \
        if ! getent group ${EXPUNGER_USER}; then groupadd ${EXPUNGER_USER}; fi; \
        if ! getent passwd ${EXPUNGER_USER}; then useradd -m -l -g ${EXPUNGER_USER} ${EXPUNGER_USER}; fi \
    ; fi

RUN echo ${EXPUNGER_USER}:${EXPUNGER_PASS} | chpasswd

USER ${EXPUNGER_USER}

# Library install
WORKDIR ${INSTALL_DIR}

COPY platform/src/requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install --user mod_wsgi

# -- DEV BUILD --
# Docket parser install
COPY --chown=${EXPUNGER_USER}:${EXPUNGER_USER} platform/docket_parser ./docket_parser
RUN pip3 install --user --editable ./docket_parser

# App install
WORKDIR ${APP_DIR}
COPY --chown=${EXPUNGER_USER}:${EXPUNGER_USER} platform/src/ .


#https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/issues/47
# -- PROD BUILD --
# Frontend install

WORKDIR ${APP_DIR}/frontend/src
COPY frontend/src/ .
#Running the command below as root, then switch back to newly created user below
USER root
# prod_build.sh will only build the front end if BACKEND_ONLY == "true"
RUN if [ "$BACKEND_ONLY" = "true" ]; then ./prod_build.sh; else echo "Dev build, frontend not compiled into django."; fi

#Change owner of the newly created files, before running the collectstatic command
RUN chown --silent --no-dereference --recursive ${EXPUNGER_USER}:${EXPUNGER_USER} ${APP_DIR}
#Then, switch back to the newly created user - not the root user
USER ${EXPUNGER_USER}

WORKDIR ${APP_DIR}
RUN python3 ./manage.py collectstatic --noinput

## -- FINAL BUILD --
ENTRYPOINT python3 ./manage.py makemigrations && python3 ./manage.py migrate && python3 ./manage.py runmodwsgi --log-to-terminal
