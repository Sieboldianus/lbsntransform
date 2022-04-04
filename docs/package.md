# Developers

## Importing lbsntransform as a package

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

### Example tool "twitterparser"

An example program `twitterparser` that uses lbsntransform as a package is available 
[here](https://gitlab.vgiscience.de/lbsn/tools/twitterparser).

The tool demonstrates an (imaginary) custom processing pipeline for Twitter data, 
stored in ZIP files on a remote server. The `twitterparser` tool will `(1)` connect to
this remote server via SSH, `(2)` pull zip files and extract the json files locally and `(3)`
transfer json files to a remote [lbsn-raw](https://gitlab.vgiscience.de/lbsn/databases/rawdb) 
or [lbsn-hll](https://gitlab.vgiscience.de/lbsn/databases/hlldb) database using lbsntransform.

Use this tool as a template or starting point and modify `__main__` to your needs.

## Contribute

lbsntransform is in an early stage of development.

You can contribute: 
 
- Feedback, submit issues for bugs etc. on [Github](https://github.com/Sieboldianus/lbsntransform)  
- Improve the concept, see [lbsn.vgiscience.org](https://lbsn.vgiscience.org/) and get [in contact](/about/) with use  
- Provide [custom mappings](/lbsntransform/docs/mappings/) for different data sources  