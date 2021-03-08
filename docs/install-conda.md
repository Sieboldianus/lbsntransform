# Installation with conda

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