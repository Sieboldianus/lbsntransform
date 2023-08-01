"""
Run Integration test based on iNaturalist/gbif data


This will check complete process of main() as if
invoked with

lbsntransform --origin 231 \
    --file_input \
    --input_path_url "https://example_url.com/inaturalist_gbif_dataset.csv" \
    --dbpassword_output "eXamPlePassWoRd" \
    --dbuser_output "postgres" \
    --dbserveraddress_output "127.0.0.1:10432" \
    --dbname_output "rawdb_test" \
    --csv_delimiter $'\t' \
    --use_csv_dictreader \
    --file_type "csv" \
    --input_lbsn_type "gbif" \
    --mappings_path "./resources/mappings/" \
    --transferlimit 10000

Requirements:
- a local postgres container with lbsn rawdb must be available
  https://gitlab.vgiscience.de/lbsn/databases/rawdb
- the database must be named rawdb_test (DATABASE_NAME=rawdb_test)

To run in dev environment, set the following variables:
- INATURALIST_URL: URL (or local Path) to gbif iNaturalist data (CSV)
- RAWDB_TEST_PW: Password for postgres database
- RAWDB_PORT: Port for lbsn raw database, e.g. 5432

Afterwards, run with `python -m tests/inaturalist_integration_test.py`
"""

import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

from lbsntransform.__main__ import main as lt_main  # type: ignore
from lbsntransform.config.config import BaseConfig  # type: ignore
from lbsntransform.input.load_data import LoadData  # type: ignore

# disable requests/urllib3 logging test urls in CI
logging.getLogger("urllib3").setLevel(logging.WARNING)


def system_integration_inaturalist_gbif():
    """Test complete method integration using main()"""
    data_source_url: Optional[str] = os.getenv("INATURALIST_URL")
    db_pass: Optional[str] = os.getenv("RAWDB_TEST_PW")
    db_port: Optional[str] = os.getenv("RAWDB_PORT")
    dbserveraddress_output: Optional[str] = os.getenv("DB_IP")
    if not dbserveraddress_output:
        dbserveraddress_output = "127.0.0.1"
    if not data_source_url:
        raise ValueError("No data source available (INATURALIST_URL)")
    # override default values with test case
    tm_cfg = BaseConfig()
    tm_cfg.origin = 231  # 23= iNaturalist, 1= gbif
    tm_cfg.is_local_input = True
    tm_cfg.local_file_type = "csv"
    if data_source_url.startswith("http"):
        tm_cfg.source_web = True
        tm_cfg.input_path = [data_source_url]
    else:
        tm_cfg.input_path = Path(data_source_url)
    tm_cfg.dbpassword_output = db_pass
    tm_cfg.dbname_output = "rawdb_test"
    tm_cfg.dbuser_output = "postgres"
    tm_cfg.input_lbsn_type = "gbif"
    tm_cfg.use_csv_dictreader = True
    tm_cfg.dbserveraddress_output = dbserveraddress_output
    if db_port:
        tm_cfg.dbserverport_output = db_port
    tm_cfg.csv_delim = "\t"
    tm_cfg.mappings_path = Path.cwd() / "resources" / "mappings/"
    tm_cfg.transferlimit = 50000

    try:
        lt_main(tm_cfg)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

    # connect to test db and check results
    dbconn, dbcursor = LoadData.initialize_connection(
        tm_cfg.dbuser_output,
        tm_cfg.dbserveraddress_output,
        tm_cfg.dbname_output,
        tm_cfg.dbpassword_output,
        tm_cfg.dbserverport_output,
    )
    if any([dbcursor, dbconn]) is None:
        raise ValueError("No db connection established")
    dbcursor.execute(
        """
        SELECT 'topical.post' AS table_name, count(*) FROM topical.post
        UNION
        SELECT 'spatial.country' AS table_name, count(*) FROM spatial.country
        UNION
        SELECT 'spatial.city' AS table_name, count(*) FROM spatial.city
        UNION
        SELECT 'social.user' AS table_name, count(*) FROM social.user
        """
    )
    results = dict(dbcursor.fetchall())

    # compare with expected results for iNaturalist/gbif first 1000 records
    assert results["spatial.city"] == 0
    assert results["topical.post"] == 999
    assert results["spatial.country"] == 72
    assert results["social.user"] == 914

    if "NO_TEAR_DOWN" in os.environ:
        return
    # cleanup step
    dbcursor.execute("""TRUNCATE social.origin CASCADE""")
    dbconn.commit()
    dbcursor.close()


if __name__ == "__main__":
    system_integration_inaturalist_gbif()
