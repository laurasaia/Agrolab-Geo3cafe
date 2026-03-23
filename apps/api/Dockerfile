FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /app/

ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY src/ ./src/

CMD [ "sh", "-c", "uv run uvicorn src.main:app --host 0.0.0.0 --port ${API_PORT:-8000}" ]

# COPY requirements.txt .

# COPY src/ ./src/

# RUN pip install --no-cache-dir -r requirements.txt

# CMD [ "sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${API_PORT:-8000}" ]
