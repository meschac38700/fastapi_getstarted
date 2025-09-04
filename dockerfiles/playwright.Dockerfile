ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION:-3.13}-bookworm AS base

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1
# Virtual env
ENV VIRTUAL_ENV=/opt/.venv

FROM base AS virtualenv

ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
ENV UV_COMPILE_BYTECODE=1

# Install dependencies:
COPY --from=ghcr.io/astral-sh/uv:0.5.13 /uv /uvx /bin/

COPY ./pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --all-extras --no-install-project --no-editable


FROM base AS test_env

ENV VBIN=$VIRTUAL_ENV/bin
ENV PLAYWRIGHT_VERSION=1.55.0
ENV APP_PORT=80

EXPOSE $APP_PORT

COPY --from=virtualenv $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VBIN:$PATH"

RUN pip install "playwright==${PLAYWRIGHT_VERSION}" && \
    playwright install --with-deps

WORKDIR /app

COPY ./src .

RUN chmod +x ./scripts/entrypoint.sh

ENTRYPOINT ["bash",  "/app/scripts/entrypoint.sh"]
