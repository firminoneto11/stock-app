FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.25 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen --no-install-project
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

ENTRYPOINT []

CMD ["sh", "-c", "coverage run -m pytest; coverage report"]
