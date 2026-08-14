FROM public.ecr.aws/docker/library/python:3.10

ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /

RUN useradd -m -u 1000 app

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    gcc \
    libssl-dev \
    libffi-dev \
    && pip install pipenv \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/app /app

COPY Pipfile* /app/

RUN cd /app && pipenv install --system --deploy

COPY . /var/www/app

WORKDIR /var/www/app

USER app

CMD ["uwsgi", "--http", "0.0.0.0:5000", "--module", "__init__:app"]