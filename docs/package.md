For in-memory conversion, it is possible to import lbsntransform as a package:

```py
import lbsntransform as lt
lt.add_processed_records(
    record)
lt.store_lbsn_records()
```

As a starting point, have a look at
[lbsntransform/__main__.py](https://gitlab.vgiscience.de/lbsn/lbsntransform/-/blob/master/lbsntransform/__main__.py),
which includes the code that is invoked on command line use.

We plan to update this section with a Jupyter Lab example notebook.