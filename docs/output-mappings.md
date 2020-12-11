**lbsntransform** can output data to a database with the [common lbsn structure](), 
called [rawdb](https://gitlab.vgiscience.de/lbsn/databases/rawdb)
or the privacy-aware version, called [hlldb](https://gitlab.vgiscience.de/lbsn/databases/hllb).

**Examples:**

To output data to rawdb:

```bash
lbsntransform --dbpassword_output "sample-key" \
              --dbuser_output "postgres" \
              --dbserveraddress_output "127.0.0.1:5432" \
              --dbname_output "rawdb" \
              --dbformat_output "lbsn"
```

The syntax for conversion to hlldb is a little bit more complex, 
since the output structure may vary to a large degree, depending 
on each use case.

!!! note
    The hlldb and structure are still in an early stage of development.
    We're beyond the initial proof of concept and are working on
    simplifying custom mappings.

To output data to hlldb:
```bash
lbsntransform --dbpassword_output "sample-key" \
              --dbuser_output "postgres" \
              --dbserveraddress_output "127.0.0.1:25432" \
              --dbname_output "hlldb" \
              --dbformat_output "hll" \
              --dbpassword_hllworker "sample-key" \
              --dbuser_hllworker "postgres" \
              --dbserveraddress_hllworker "127.0.0.1:15432" \
              --dbname_hllworker "hllworkerdb" \
              --include_lbsn_objects "origin,post" \
```

Above, a separate connection to a "hll_worker" database is provided.
It is used to make hll calculations (union, hashing etc.). No items
will be written to this database, a read_only user will suffice. A
[Docker container with a predefined user](https://gitlab.vgiscience.de/lbsn/databases/pg-hll-empty) 
is available.

Having two hll databases, one for calculations and one for storage means
that concerns can be separated: There is no need for hlldb to receive any
raw data. Likewise, the hll worker does not need to know contextual data,
for union of specific hll sets. Such a setup improves rubustness and privacy.
It further allows to separate processing into individual components.

If no hll worker is available, hlldb may be used.

Use `--include_lbsn_objects` to specify which input data you want to convert to 
the privacy aware version. For example, `--include_lbsn_objects "origin,post"`
would process [lbsn objects](https://lbsn.vgiscience.org/structure/) 
of type origin and post (default).

Use `--include_lbsn_bases` to specify which output data you want to convert to.

We call this "bases", and they are defined in output mappings in
[lbsntransform/input/field_mapping_lbsn.py](/api/output/hll/hll_bases.html),

Bases can be separated by comma and may include:

- Temporal Facet:  
    - `monthofyear`
    - `month`
    - `dayofmonth`
    - `dayofweek`
    - `hourofday`
    - `year`
    - `month`
    - `date`
    - `timestamp`

- Spatial Facet:  
    - `country`
    - `region`
    - `city`
    - `place`
    - `latlng`

- Social Facet:  
    - `community`

- Topical Facet:  
    - `hashtag`
    - `emoji`
    - `term`

- Composite Bases:  
    - `_hashtag_latlng`
    - `_term_latlng`
    - `_emoji_latlng`


For example:
```bash
lbsntransform --include_lbsn_bases hashtag,place,date,community
```

would fill/update entries of the hlldb structures:  
- topical.hashtag
- spatial.place
- temporal.date
- social.community

This name refers to `schema.table`.

It is possible to define own output hll db mappings. The best place
to start is [lbsntransform/input/field_mapping_lbsn.py](/api/output/hll/hll_bases.html).
Have a look at the pre-defined bases and add any additional needed. It is recommended
to use inheritance. After adding your own mappings, the hlldb must be prepared with
respective table structures. Have a look at the 
[predefined structures available](https://gitlab.vgiscience.de/lbsn/structure/hlldb).

