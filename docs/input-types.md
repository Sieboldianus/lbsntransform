# Input type: File, URL, or Database?

lbsntransform can read data from different common types of data sources.

The two main input types to distinguish are input from files and databases.

The following cli arguments are available for the two types.

!!! note
    At the moment, validation of CLI arguments is only done rudimentary. This
    makes it necessary to carefully check parameters. Expect that errors may
    be misleading. If in doubt, have a look at parameter processing in
    the [config module](../api/config/config.html).
    
## File and URL input 

* activated by `--file_input`
* json files `--file_type json`
    * stacked `--is_stacked_json`
      The typical form for json is `[{json1},{json2}]`. If `--is_stacked_json` is set,
      jsons in the form of `{json1}{json2}` (no comma) can be imported.
    * line separated `--is_line_separated_json`
      If this flag is used, lbsntransform expects one json per line (separated with a line break).
* csv files `--file_type csv`
    * Set CSV delimiter with `--csv_delimiter`, common types are e.g.:
        * Comma: `','` (default)
        * Semi-colon: `';'`
        * Tab: `$'\t'`
* Additional flags for file input:
    * `--input_path_url` the folder, path or url to read from, e.g.:
        * `--input_path_url 01_Input` Read from the relative subfolder "01_Input" (default).
        * `--input_path_url ~/data/` Read from the user's home folder "data".
        * `--input_path_url /c/tmp/data` Read from a WSL mounted subdir from Windows.
    * `--recursive_load` to recursively process local sub directories (default depth: 2).
    * `--skip_until_file x` to process all files until a file name with name `x` is found
    * `--zip_records` Allows to zip records from multiple sources using semi-colon (`;`), e.g.:
        * `--input_path_url "https://mypage.org/dataset_col1.csv;https://mypage.org/dataset_col2.csv"`
          Will process records from both csv files parallel, by zipping files.

!!! note "Note <code>--input_path_url</code>"
    To not be confused, this flag is used to provide _either_ a path _or_ a url to data. 
    
    - can also be list of urls (when using `--zip_records`)
    - paths can be relative or absolute
    - they will be parsed using `pathlib.Path`, which is OS independent.
    
## Database input (Postgres)

* activated by default
* `--dbuser_input "postgres"` the name of the dbuser
* `--dbserveraddress_input "127.0.0.1:5432"` the name and (optional) the port to use. The default postgres port is `5432`.
* `--dbname_input "rawdb"` the name of the database.
* `--dbpassword_input "mypw` the password to use when connecting.
* `--dbformat_input "lbsn"` the format of the database. Currently, only "lbsn" and "json" are supported.
* Additional flags for db input:
    - `--records_tofetch 1000` If retrieving from a db, limit the 
      number of records to fetch per batch. Defaults to 10k.
    - `--startwith_db_rownumber xyz` To resume processing from an arbitrary ID.
      If input db type is "LBSN", provide the primary key to start from (e.g. post_guid, place_guid etc.). 
      This flag will only work if processing a single lbsnObject (e.g. lbsnPost).
    - `--endwith_db_rownumber xyz` To stop processing at a particular row-id.
    - `--include_lbsn_objects` If processing from lbsn rawdb, provide a comma separated list of 
      [lbsn objects](https://lbsn.vgiscience.org/structure/) to include. May contain any of:  
      `origin,country,city,place,user_groups,user,post,post_reaction,event`
      <br/><br/>
      
    !!! note "Note <code>--include_lbsn_objects</code>"
        Excluded objects will not be queried, but empty objects may be created due to referenced 
        foreign key relationships. Defaults to `origin,post`.
        
See the full list of CLI arguments [here](/argparse/args/).