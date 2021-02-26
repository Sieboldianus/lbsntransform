FROM continuumio/miniconda3:latest as build-stage

WORKDIR /app

COPY lbsntransform/ ./lbsntransform/
COPY resources/ ./resources/
COPY *.py environment.yml README.md ./

RUN conda update -n base -c defaults conda \
    && conda config --env --set channel_priority strict
RUN conda env create -f ./environment.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack -y

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n lbsntransform -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack

FROM python:alpine as runtime

# Copy /venv from the previous stage:
COPY --from=build-stage /venv /venv

# When image is run, run the code with the environment
# activated:
SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && lbsntransform"
