# Windows

There are many ways to install python tools:

1. The recommended way to install the package is with `pip install lbsntransform`
2. For Windows users, an alternative is to download the newest pre-compiled build from [releases](../../releases) and run `lbsntransform.exe`
3. If you have problems with dependencies under windows, use [Gohlke wheels](<https://www.lfd.uci.edu/~gohlke/pythonlibs/>) or create an environment with with conda package manager, install all dependencies manually and then run `pip install lbsntransform --no-deps`

# Linux

For most Linux users, it is recommended first creating some type of virtual environment, and then install lbsntransform in this virtual env, e.g.:
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

If you have conda package manager you can install lbsntransform dependencies, OS independent, with the `environment.yml` that is available in the lbsntransform repository:

```bash
git clone https://github.com/Sieboldianus/lbsntransform.git
cd lbsntransform
conda env create -f environment.yml
```

..and then install lbsntransform directly:
```bash
conda activate lbsntransform
python setup.py install --no-deps
```


