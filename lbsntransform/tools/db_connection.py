# -*- coding: utf-8 -*-
"""Provides functions to connect to Postgres DB

"""

import datetime
import getpass
import logging
import sys

import psycopg2
import psycopg2.extras

LOG = logging.getLogger()


class DBConnection():
    """ Class for connectiong to Postgres. """

    def __init__(self, serveraddress=None, dbname=None,
                 user=None, password=0, readonly=False,
                 sslmode='prefer', port=5432):
        """Initialize DBConnection object with attributes, if passed. """
        self.serveraddress = serveraddress
        self.dbname = dbname
        self.user = user
        self.password = password
        self.readonly = readonly
        self.sslmode = sslmode  # Choose 'disable' to connect without ssl
        self.port = port

    def connect(self):
        """Database config. """
        conf = {
            "host": self.serveraddress,
            "dbname": self.dbname,
            "user": self.user,
            "sslmode": self.sslmode,
            "port": self.port
        }
        # Connect to database
        if self.password == 0:
            promt_txt = f"Enter the password for {conf['user']}: "
            if sys.stdin.isatty():
                conf["password"] = getpass.getpass(prompt=promt_txt)
            else:
                print(promt_txt)
                conf["password"] = sys.stdin.readline().rstrip()
        else:
            conf["password"] = self.password
        # define connection string
        conn_string = f"host='{conf['host']}'" \
                      f"dbname='{conf['dbname']}'" \
                      f"user='{conf['user']}'" \
                      f"password='{conf['password']}'" \
                      f"sslmode='{conf['sslmode']}'" \
                      f"port='{conf['port']}'" \
                      f"application_name='LBSN Batch Transfer'"
        # get a connection, if a connect cannot be made an
        # exception will be raised here
        try:
            conn = psycopg2.connect(conn_string)
        except Exception as err:
            print(err)
            sys.exit()
        # activate dict to hstore conversion globally
        psycopg2.extras.register_hstore(conn, globally=True)
        # conn.cursor will return a cursor object,
        # you can use this cursor to perform queries
        cursor = conn.cursor()
        dnow = datetime.datetime.now()
        LOG.info(f'{dnow.strftime("%Y-%m-%d %H:%M:%S")} '
                 f'- Connected to {self.dbname}')
        return conn, cursor
