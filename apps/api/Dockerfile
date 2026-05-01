FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md serve_api.py /app/
COPY src /app/src
COPY apps/api /app/apps/api
COPY adversary /app/adversary
COPY data /app/data
COPY benchmark /app/benchmark
COPY results /app/results
RUN pip install --no-cache-dir .

EXPOSE 8011
CMD ["python", "serve_api.py", "--host", "0.0.0.0", "--port", "8011"]
