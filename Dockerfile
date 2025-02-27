FROM python:3.12-slim

WORKDIR /app

# install build dependencies
COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /uvx /bin/

# install dependencies
COPY uv.lock /app/
COPY pyproject.toml /app/
RUN uv sync --frozen --no-cache

# copy log config
COPY log_conf.yaml /app/

# copy migrations
COPY alembic.ini /app/
COPY migrations /app/migrations

# copy application
COPY app /app/app

# venv activate 
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "app.server:create_app", "--host", "0.0.0.0", "--factory"]
