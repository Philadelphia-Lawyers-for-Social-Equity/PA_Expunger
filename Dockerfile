FROM debian:stable

ENV INSTALL_DIR /srv/plse/install
ENV APPDIR /srv/plse/expunger
ENV REACT_APP_BACKEND_HOST http://localhost:8000

ARG EXPUNGER_USER
ARG EXPUNGER_PASS
ARG EXPUNGER_KEY
ARG DJANGO_SETTINGS_MODULE

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
    python-dev \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
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
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y -qq nodejs
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

RUN mkdir -p ${APPDIR}/static
RUN chown --silent --no-dereference --recursive ${EXPUNGER_USER}:${EXPUNGER_USER} ${APPDIR}
USER ${EXPUNGER_USER}

# Library install
WORKDIR ${INSTALL_DIR}
COPY platform/docket_parser/requirements.txt .
RUN pip3 install -r requirements.txt

COPY platform/src/requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install --user mod_wsgi

# -- DEV BUILD --
# Docket parser install

WORKDIR ${INSTALL_DIR}/docket_parser
COPY platform/docket_parser/ .
RUN pip3 install ./

# App install
WORKDIR ${APPDIR}
COPY platform/src/ .


# TODO: make this only happen in production
#https://github.com/Philadelphia-Lawyers-for-Social-Equity/docket_dashboard/issues/47
# -- PROD BUILD --
# Frontend install

WORKDIR ${APPDIR}/frontend/src
COPY frontend/src/ .
USER root
RUN yarn install --non-interactive --silent --production
RUN yarn build
USER ${EXPUNGER_USER}
WORKDIR ${APPDIR}
RUN python3 ./manage.py collectstatic --noinput

## -- FINAL BUILD --
ENTRYPOINT python3 ./manage.py makemigrations && python3 ./manage.py migrate && python3 ./manage.py runmodwsgi --log-to-terminal
