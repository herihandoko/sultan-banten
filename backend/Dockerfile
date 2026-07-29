# SIAGAPIM — Flask API
FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq5 curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh \
  && mkdir -p instance

ENV FLASK_APP=wsgi:app
ENV PYTHONUNBUFFERED=1

EXPOSE 5001

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:5001", "-w", "2", "--timeout", "120", "wsgi:app"]
