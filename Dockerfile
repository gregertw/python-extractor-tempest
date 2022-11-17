FROM python:3.10-slim-buster as python

RUN useradd -ms /bin/bash extractor
RUN mkdir /src
WORKDIR /src
RUN apt-get update

FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY . ./
RUN poetry install --no-interaction --no-ansi -vv

FROM python as runtime
ENV PATH="/src/.venv/bin:$PATH"
COPY --from=poetry /src /src
WORKDIR /src
CMD ["python", "tempest_extractor/__main__.py", "config.yaml"]