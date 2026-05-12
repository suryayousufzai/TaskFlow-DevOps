# Stage 1: Builder
# we use a slim python image to keep things light
FROM python:3.12-slim AS builder

WORKDIR /build

# need build-essential to compile some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# install all python dependencies into /install so we can copy them later
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# Stage 2: Runtime
# fresh slim image, no build tools needed here
FROM python:3.12-slim AS runtime

# running as non-root is a good security habit
RUN groupadd -r taskflow && useradd -r -g taskflow taskflow

WORKDIR /app

# grab the installed packages from the builder stage
COPY --from=builder /install /usr/local

# copy the actual app code
COPY app/ ./app/
COPY run.py .

# sqlite needs somewhere to store the database file
RUN mkdir -p /data && chown -R taskflow:taskflow /app /data

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=sqlite:////data/taskflow.db \
    SECRET_KEY=change-me-in-production \
    PORT=5000

USER taskflow

EXPOSE 5000

# docker will ping this to check if the app is still alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# start the app with gunicorn, 2 workers + 2 threads should be fine for now
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", \
     "--timeout", "60", "--access-logfile", "-", "run:app"]
