"""
Run Integration test based on yfcc data


This will check complete process of main() as if
invoked with

lbsntransform --origin 21 \
    --file_input \
    --input_path_url "https://example_url.com/yfcc100m_dataset.csv;https://example_url.com/yfcc100m_places.csv" \
    --dbpassword_output "eXamPlePassWoRd" \
    --dbuser_output "postgres" \
    --dbserveraddress_output "127.0.0.1:10432" \
    --dbname_output "rawdb" \
    --csv_delimiter $'\t' \
    --file_type "csv" \
    --zip_records \
    --mappings_path "./resources/mappings/" \
    --transferlimit 10000

Requirements:
- a local postgres container with lbsn rawdb must be available
https://gitlab.vgiscience.de/lbsn/databases/rawdb
- the database must be named rawdb_test
"""

import logging
import os
import sys
import traceback
from pathlib import Path

from lbsntransform.__main__ import main as lt_main  # type: ignore
from lbsntransform.config.config import BaseConfig  # type: ignore
from lbsntransform.input.load_data import LoadData  # type: ignore

# disable requests/urllib3 logging test urls in CI
logging.getLogger("urllib3").setLevel(logging.WARNING)


def system_integration_yfcc():
    """Test complete method integration using main()"""
    data_source_url: str = os.getenv("YFCC_URL")
    db_pass: str = os.getenv("RAWDB_TEST_PW")
    db_port: str = os.getenv("RAWDB_PORT")
    dbserveraddress_output: str = os.getenv("DB_IP")
    if not dbserveraddress_output:
        dbserveraddress_output = "127.0.0.1"
    # override default values with test case
    tm_cfg = BaseConfig()
    tm_cfg.origin = 21  # 2= Flickr, 1= YFCC
    tm_cfg.is_local_input = True
    tm_cfg.local_file_type = "csv"
    tm_cfg.input_path = data_source_url.split(";")
    tm_cfg.source_web = True
    tm_cfg.dbpassword_output = db_pass
    tm_cfg.dbname_output = "rawdb_test"
    tm_cfg.dbuser_output = "postgres"
    tm_cfg.dbserveraddress_output = dbserveraddress_output
    tm_cfg.dbserverport_output = db_port
    tm_cfg.csv_delim = "\t"
    tm_cfg.zip_records = True
    tm_cfg.mappings_path = Path.cwd() / "resources" / "mappings/"
    tm_cfg.transferlimit = 10000

    try:
        lt_main(tm_cfg)
        # sys.exit(0)
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
    dbcursor.execute(
        """
        SELECT 'topical.post' AS table_name, count(*) FROM topical.post
        UNION
        SELECT 'spatial.country' AS table_name, count(*) FROM spatial.country
        UNION
        SELECT 'spatial.city' AS table_name, count(*) FROM spatial.city
        UNION
        SELECT 'spatial.place' AS table_name, count(*) FROM spatial.place
        UNION
        SELECT 'social.user' AS table_name, count(*) FROM social.user
        """
    )
    results = dict(dbcursor.fetchall())

    # compare with expected results for YFCC first 10000 records
    assert results["spatial.city"] == 1265
    assert results["topical.post"] == 3332
    assert results["spatial.country"] == 245
    assert results["social.user"] == 2991

    # cleanup step
    dbcursor.execute("""TRUNCATE social.origin CASCADE""")
    dbconn.commit()
    dbcursor.close()


if __name__ == "__main__":
    system_integration_yfcc()
