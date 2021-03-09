# Examples

lbsntransform has a Command Line Interface (CLI) that can be used to convert many 
input formats to common lbsnstructure, including to its privacy-aware hll implementation.


!!! Note
    Substitute bash linebreak character `\` in examples below with `^` if you're on Windows command line

## Basic examples

Key to mappings in lbsntransform is the origin id, which refers to the different mappings specified in modules `input/mappings/*.py`. For example,
id `3` refers to Twitter (`field_mapping_twitter.py`).

If you've retrieved Twitter jsons from the offocial API, place those files somewhere in a subfolder `.01_Input/` and run the following:

```bash
lbsntransform --origin 3 \
    --file_input \
    --file_type 'json' \
    --transferlimit 1000 \
    --csv_output \
    --mappings_path ./resources/mappings/

```

lbsntransform will then create a subfolder `.02_Output/` and store converted data as CSV (specified with `--csv_output` flag).

* `--transferlimit 1000` means: skip transfer after 1000 lbsn records
* `--file_input`: read from local files (and not from database). Default local input is subfolder `./01_Input/`. This path can be modified with the flag `--input_path_url my-input-path`
* `--file_type 'json'` refers to the file ending to look for in `.01_Input/` folder

If your files are spread across subdirectories in (e.g.) `./01_Input/`, add `--recursive_load` flag.

## Flickr YFCC100m

A specific mapping is provided for the [YFCC100m Dataset](https://multimediacommons.wordpress.com/yfcc100m-core-dataset/).


The YFCC100m Dataset consists of multiple files, with the core dataset of 100 Million 
Flickr photo metadata records (yfcc100m_dataset.csv) and several "expansion sets".


The only expansion-set that is available for mapping is places-expansion (yfcc100m_places.csv).


Both photo metadata and places metadata can be processed parrallel, by using `--zip_records`.


Before executing the following, make sure you've started the [lbsn-raw database docker](https://gitlab.vgiscience.de/lbsn/databases/rawdb). 
This includes the postgres implementation of the common lbsn structure format. You 
can run the docker db container on any host, but we suggest testing your setup locally 
- in this case, `127.0.0.1` refers to _localhost_ and port `15432` (the default for 
lbsn-raw).


```bash
lbsntransform --origin 21 \
    --file_input \
    --input_path_url "https://myurltoflickrymcc.dataset.org/yfcc100m_dataset.csv;https://myurltoflickrymcc.dataset.org/flickr_yfcc100m/yfcc100m_places.csv" \
    --dbpassword_output "your-db-password" \
    --dbuser_output "postgres" \
    --dbserveraddress_output "127.0.0.1:15432" \
    --dbname_output "rawdb" \
    --csv_delimiter $'\t' \
    --file_type "csv" \
    --zip_records \
    --skip_until_record 7373485 \
    --transferlimit 10000 \
    --mappings_path ./resources/mappings/
```

In the example above,

```bash
--skip_until_record 7373485
```
.. is used to skip input records up to record `7373485`. This is an example on how to continue processing (e.g. if your previous transform job was aborted for any reason).


Also, transfer is limited to first 10000 records:

```bash
--transferlimit 10000
```

If you have stored the Flickr-dataset locally, simply replace the urls with:

```bash
--input_path_url "/data/flickr_yfcc100m/"
```


## Privacy-aware output (HyperLogLog)

We've developed a privacy-aware implementation of lbsn-raw format, based based on 
the probabilistic datastructure HyperLogLog and the postgres implementation from 
[Citus](https://github.com/citusdata/postgresql-hll).

Two preparations steps are necessary:

* Prepare a postgres database with the HLL version of lbsnstructure. You can use 
  the [lbsn-hll database docker](https://gitlab.vgiscience.de/lbsn/databases/hlldb)

* Prepare a read-only (empty) database with Citus HyperLogLog extension installed. 
  You can use the [hll importer docker](https://gitlab.vgiscience.de/lbsn/tools/importer)


We've designed this rather complex setup to separate concerns:

- the importer db (called `hllworkerdb` in the command below) will be used by lbsntransform 
  to calculate hll `shards` from raw data
- it will not store any data, nor will it get any additional (privacy-relevant) information.
- Shards are calculated in-memory and returned. The importer is prepared with global 
  hll-settings that must not change during the whole lifetime of the final output.

For example, as a means of additional security, before creating shards, distinct 
values can be one-way-hashed. This hashing can be improved using a `salt` that is 
only known to **importer**.

Finally, as a result, output hll db will not retrieve any privacy-relevant data because 
this is removed before transmission.

!!! Note
    Depending on chosen `bases` and the type of input data, data may still contain 
    privacy sensitive references. Have a look at the [lbsn-docs](https://lbsn.vgiscience.org) 
    for further information.

To convert YFCC100m photo metadata and places and transfer to a local hll-db, use:


```bash
lbsntransform --origin 21 \
    --file_input \
    --input_path_url "/data/flickr_yfcc100m/" \
    --dbpassword_output "your-db-password" \
    --dbuser_output "postgres" \
    --dbserveraddress_output "127.0.0.1:25432" \
    --dbname_output "hlldb" \
    --dbformat_output "hll" \
    --dbpassword_hllworker "your-db-password" \
    --dbuser_hllworker "postgres" \
    --dbserveraddress_hllworker "127.0.0.1:20432" \
    --dbname_hllworker "hllworkerdb" \
    --csv_delimiter $'\t' \
    --file_type "csv" \
    --zip_records \
    --mappings_path ./resources/mappings/
```
