FROM python:3.14-slim
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
  UV_NO_CACHE=1 \
  UV_NO_DEV=1

RUN groupadd --force --gid $GID lonk \
    && useradd --non-unique --home-dir /opt/lonk --create-home --uid $UID --gid $GID --comment "Application" lonk

USER lonk

WORKDIR /opt/lonk

COPY --chown=lonk:lonk pyproject.toml /opt/lonk
COPY --chown=lonk:lonk uv.lock /opt/lonk
RUN --mount=from=ghcr.io/astral-sh/uv:0.12.5,source=/uv,target=/bin/uv \
    uv venv \
    && uv pip install pip \
    && uv sync

# don't copy all of the current directory (might contain stuff like build cache / -config or other
# state)
# alternatively, one might add a very generous `.dockerignore`
COPY --chown=lonk:lonk lonk lonk

EXPOSE 5000

ENV FLASK_APP=lonk.app:app \
    FLASK_RUN_HOST=0.0.0.0

CMD [".venv/bin/flask", "run"]
