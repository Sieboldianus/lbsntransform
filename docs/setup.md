# Installation
## Installation with conda

This is the recommended way for all systems.

This approach is independent of the OS used.

If you have conda package manager, you can install lbsntransform dependencies 
with the `environment.yml` that is available in the lbsntransform repository:

```yaml
{!../environment.yml!}
```

1. Create a conda env using `environment.yml`

```bash
git clone https://github.com/Sieboldianus/lbsntransform.git
cd lbsntransform
# not necessary, but recommended:
conda config --env --set channel_priority strict
conda env create -f environment.yml
```

2. Install lbsntransform without dependencies

```bash
conda activate lbsntransform
```

Either, use the release version from pypi. This will create a static installation that needs
to be manually upgraded when new package versions appear.

```bash
pip install lbsntransform --no-deps --upgrade
```

Or use pip `--editable`, linking the lbsntransform folder:

```bash
pip install --no-deps --editable .
```

This is the recommended way if you want to edit files, or use the latest commits from the repository.

The `lbsntransform` package will be directly linked to the folder.

!!! note "Why isn't the package available on conda-forge?"
    This is planned to happen in one of the next versions..
    
## Docker

If you have Docker, and if you do not want to develop or make changes to lbsntransform,
using our Dockerimage may be an option.

!!! note
    The Docker Image is in an early stage. Providing input data is only
    possible through URL, from another database, or through 
    local bind mounting data (e.g. CSVs) into the container (see note at end).

You can use the latest Dockerimage to directly run lbsntransform in a container:

First, pull the image.
```bash
docker pull registry.gitlab.vgiscience.org/lbsn/lbsntransform:latest
docker tag registry.gitlab.vgiscience.org/lbsn/lbsntransform:latest lbsntransform
```

Then run it.
```bash
docker run \
    --rm \
    lbsntransform \
    --version
```

!!! note
    Replace `--version` with the CLI commands for your use case.
    
Or, use the Dockerfile in `docker/Dockerfile` to build the image yourself.

```dockerfile
{!../docker/Dockerfile!}
```

Example:
```bash
docker build -t lbsntransform -f docker/Dockerfile .
docker run \
    --rm \
    lbsntransform \
    --version
```

### Mounting data

If you want to use custom mappings, or read data from CSV (etc.),
mount these external files on runtime into the container.

Example:
```bash
docker run \
    --rm \
    --volume $(pwd)/data.csv:/data/data.csv \
    --volume $(pwd)/resources/mappings:/mappings \
    lbsntransform \
    --mappings_path /mappings/ \
    ...
```

## Alternatives: Windows and Linux

### Windows

There are many ways to install python tools, in Windows this can become particularly frustrating.

1. For most Windows users, the recommended way is to install lbsntransform with [conda package manager](#installation-with-conda)
2. You can also use the [Docker](#docker) approach in Windows, e.g. in combination with Windows Subsystem for Linux (WSL)
3. If you _need_ to install with pip in Windows, a possible approach is to install all dependencies first (use [Gohlke wheels] 
   if necessary) and then install lbsntransform with 

```bash
pip install lbsntransform --no-deps
```

### Linux

!!! note
    Use of pip can be problematic, even on Linux. Some sub-dependencies outside python [cannot 
    be managed by pip][1], such as `libpq-dev`, which is required by [psycopg2]. 
    Use [conda](#conda) if you're new to python package managers. You've been warned.
    
For most Linux users, it is recommended to first create some type of virtual environment, 
and then install lbsntransform in the virtual env, e.g.:

```bash
apt-get install -y libpq-dev # required for psycopg2
apt-get install python3-venv # required for virtual env
python3 -m venv lbsntransform_env
source ./lbsntransform_env/bin/activate
pip install lbsntransform
```

You can also directly install the latest release of lbsntransform with pip:

```bash
pip install lbsntransform
```

..or, clone the repository and install lbsntransform directly:

```bash
git clone https://github.com/Sieboldianus/lbsntransform.git
cd lbsntransform
python setup.py install
```

[1]: https://stackoverflow.com/q/27734053/4556479#comment43880476_27734053
[psycopg2]: https://www.psycopg.org/install/
[Gohlke wheels]: https://www.lfd.uci.edu/~gohlke/pythonlibs/