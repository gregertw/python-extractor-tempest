FROM python:3.10-slim as python

RUN useradd -s /bin/bash -r extractor
RUN mkdir /src
WORKDIR /src
RUN apt update && apt upgrade -y
RUN apt-get install gcc python3-dev -y
RUN pip install --no-cache-dir poetry
COPY . ./
RUN poetry install --no-interaction --no-ansi -vv

FROM python as runtime
ENV PATH="/src/.venv/bin:$PATH"
COPY --from=python /src /src
WORKDIR /src
CMD ["python", "tempest_extractor/__main__.py", "config.yaml"]