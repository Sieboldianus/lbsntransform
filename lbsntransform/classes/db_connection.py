# -*- coding: utf-8 -*-
"""Provides functions to connect to Postgres DB

"""

import getpass
import logging
import sys
import datetime
import psycopg2

LOG = logging.getLogger()

class DBConnection():
    """ Class for connectiong to Postgres. """
    def __init__(self, serveradress=None, dbname=None,
                 user=None, password=0, readonly=False,
                 sslmode='prefer'):
        """Initialize DBConnection object with attributes, if passed. """
        self.serveradress = serveradress
        self.dbname = dbname
        self.user = user
        self.password = password
        self.readonly = readonly
        self.sslmode = sslmode # Choose 'disable' to connect without ssl

    def connect(self):
        """Database config. """
        conf = {
            "host":self.serveradress,
            "dbname":self.dbname,
            "user":self.user,
            "sslmode":self.sslmode
        }
        ## Connect to database
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
                      f"application_name='LBSN Batch Transfer'"
        # get a connection, if a connect cannot be made an exception will be raised here
        try:
            conn = psycopg2.connect(conn_string)
        except Exception as err:
            print(err)
            sys.exit()
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        cursor = conn.cursor()
        dnow = datetime.datetime.now()
        LOG.info(f'{dnow.strftime("%Y-%m-%d %H:%M:%S")} '
                 f'- Connected to {self.dbname}')
        return conn, cursor
