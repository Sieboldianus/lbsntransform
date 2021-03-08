# Windows

There are many ways to install python tools, in Windows this can become particularly frustrating.

1. For most Windows users, the recommended way is to install lbsntransform with [conda package manager](/install-conda/)
2. You can also use the [Docker](/install-docker/) approach in Windows, e.g. in combination with Windows Subsystem for Linux (WSL)
3. If you _need_ to install with pip in Windows, a possible approach is to install all dependencies first (use [Gohlke wheels] 
   if necessary) and then install lbsntransform with 

```bash
pip install lbsntransform --no-deps
```

# Linux

!!! note
    Use of pip can be problematic, even on Linux. Some sub-dependencies outside python [cannot 
    be managed by pip][1], such as `libpq-dev`, which is required by [psycopg2]. 
    Use [conda](/install-conda/) if you're new to python package managers. You've been warned.
    
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