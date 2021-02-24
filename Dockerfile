FROM continuumio/miniconda3:latest

WORKDIR /app

COPY lbsntransform/ ./lbsntransform/
COPY resources/ ./resources/
COPY *.py environment.yml README.md ./

RUN conda config --env --set channel_priority strict

RUN conda env create -f ./environment.yml

RUN conda run -n lbsntransform pip install --no-deps --upgrade .

#SHELL ["conda", "run", "-n", "lbsntransform", "/bin/bash", "-c"]

ENTRYPOINT ["conda", "run", "-n", "lbsntransform", "lbsntransform"]
