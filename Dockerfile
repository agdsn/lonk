FROM python:3.9-buster
ARG UID=1000
ARG GID=1000
ENV LANG=C.UTF-8 \
  DEBIAN_FRONTEND=noninteractive \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.5

COPY docker/etc/apt /etc/apt

# Install Debian packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        libpq5 \
    && apt-get -y upgrade \
    && apt-get -y dist-upgrade \
    && apt-get clean \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
    && pip install "poetry==$POETRY_VERSION"

RUN groupadd --force --gid $GID lonk \
    && useradd --non-unique --home-dir /opt/lonk --create-home --uid $UID --gid $GID --comment "Application" lonk

USER lonk

WORKDIR /opt/lonk

COPY --chown=lonk:lonk pyproject.toml /opt/lonk
COPY --chown=lonk:lonk poetry.lock /opt/lonk
RUN poetry install --no-dev  # Creates a virtualenv automatically

COPY --chown=lonk:lonk . .

EXPOSE 5000

# see https://flask.palletsprojects.com/en/1.1.x/cli/#setting-command-options
ENV FLASK_APP=lonk.app:app \
    FLASK_RUN_HOST=0.0.0.0
CMD ["poetry run uwsgi"]
