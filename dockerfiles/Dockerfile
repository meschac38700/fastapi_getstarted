# -------------------- Base image --------------------
ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION:-3.13}-slim-bookworm AS base

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# -------------------- Python dependencies --------------------
FROM python:${PYTHON_VERSION:-3.13}-slim AS virtualenv

ENV VIRTUAL_ENV=/opt/.venv
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
ENV UV_COMPILE_BYTECODE=1

# Install dependencies:
COPY --from=ghcr.io/astral-sh/uv:0.7.14 /uv /uvx /bin/

COPY ./pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project --no-editable;

# -------------------- Python final image --------------------
FROM base AS runtime

# set environment variables
ENV USER=appuser
ENV USER_HOME_DIRECTORY=/home/${USER}
ENV APP_DIR=${USER_HOME_DIRECTORY}/app/www
# Virtual env
ENV VIRTUAL_ENV=/opt/.venv
ENV APP_PORT=80
ENV VBIN=$VIRTUAL_ENV/bin
ENV PYTHONPATH=$VBIN
RUN useradd --user-group --create-home --uid 1000 ${USER}

# APP_PORT is an environment variable, used in entrypoint.sh file to run server.
ARG APP_EXPOSE_PORT=$APP_PORT

EXPOSE ${APP_EXPOSE_PORT}

# curl is needed for app health check
RUN apt-get update -y \
 && apt-get -y install apt-utils \
 && apt-get -y install curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the environment, but not the source code
COPY --from=virtualenv --chown=${USER}:${USER} $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VBIN:$PATH"

WORKDIR ${APP_DIR}

USER ${USER}

COPY --chown=${USER}:${USER} ./src .

RUN chmod +x ./scripts/entrypoint.sh  && \
    chmod +x ./scripts/entrypoint-celery.sh && \
    chmod +x ./scripts/entrypoint-beat.sh \
