FROM ghcr.io/astral-sh/uv:python3.8-bookworm-slim
LABEL authors="irinanechetnaya"

COPY . /app
WORKDIR /app
# RUN pip install git+https://github.com/lyst/lightfm.git
ENV PYTHON_VERSION=python3
ENV PYTHONUNBUFFERED=1
RUN uv sync --python $PYTHON_VERSION --frozen --no-cache

# CMD [".venv/bin/python3", "-m", "uvicorn", "app.main:app"]
CMD [".venv/bin/python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

