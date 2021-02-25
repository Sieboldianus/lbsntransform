FROM python:slim

RUN set -ex; \
    \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
    ;

COPY lbsntransform/ ./lbsntransform/
COPY resources/ ./resources/
COPY setup.py README.md ./

RUN pip install --upgrade pip; \
    pip install psycopg2-binary

RUN pip install --ignore-installed --editable .

RUN apt-get purge -y \
        build-essential \
    ; \
    apt-get autoremove -y \
    ; \
    rm -rf /var/lib/apt/lists/* \
    ;

ENTRYPOINT ["lbsntransform"]
