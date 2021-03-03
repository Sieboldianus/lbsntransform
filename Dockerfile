FROM python:slim

COPY lbsntransform/ ./lbsntransform/
COPY resources/ ./resources/
COPY setup.py README.md ./

RUN set -ex; \
    \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
    ; \
    pip install --upgrade pip; \
    pip install psycopg2-binary; \
    pip install --ignore-installed --editable . \
    ; \
    apt-get purge -y \
        build-essential \
    ; \
    apt-get autoremove -y \
    ; \
    rm -rf /var/lib/apt/lists/*;

ENTRYPOINT ["lbsntransform"]
