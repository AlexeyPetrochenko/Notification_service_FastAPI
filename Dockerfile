FROM python:3.12-slim

WORKDIR /app

# install build dependenses
COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /uvx /bin/

# install dependenses
COPY uv.lock /app/
COPY pyproject.toml /app/
RUN uv sync --frozen --no-cache

# copy migrationsp
COPY alembic.ini /app/
COPY migrations /app/migrations

# copy application
COPY .env  /app/
COPY app /app/app

# venv activate 
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "app.server:create_app", "--host", "0.0.0.0", "--factory"]
