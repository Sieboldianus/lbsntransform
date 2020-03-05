# Windows

There are many ways to install python tools, in Windows this can become particularly frustrating.

1. For most Windows users, the recommended way is to install lbsntransform with [conda package manager](#installation-with-conda)
2. If you _need_ to install with pip in Windows, a possible approach is to install all dependencies first (use [Gohlke wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/) if necessary) and then install lbsntransform with 

        pip install lbsntransform --no-deps

# Linux

For most Linux users, it is recommended to first create some type of virtual environment, and then install lbsntransform in the virtual env, e.g.:

```bash
apt-get install python3-venv
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

# Installation with conda

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
conda env create -f environment.yml
```

<span>2.</span> Install lbsntransform without dependencies

```bash
conda activate lbsntransform
python setup.py install --no-deps
```


