# -*- coding: utf-8 -*-

import getpass
import logging
import psycopg2
import sys
import datetime

log = logging.getLogger()

class dbConnection():  
    def __init__(self, serveradress=None, dbname=None,
                 user=None,password=0,readonly=False, sslmode='prefer'):
        self.serveradress = serveradress
        self.dbname = dbname
        self.user = user
        self.password = password
        self.readonly = readonly
        self.sslmode = sslmode #Choose 'disable' to connect without ssl
        
    def connect(self):
        ##Database config
        conf = {
            "host":self.serveradress,
            "dbname":self.dbname,
            "user":self.user,
            "sslmode":self.sslmode
        }
        ##Connect to database
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
        conn_string = f"host='{conf['host']}' dbname='{conf['dbname']}' user='{conf['user']}' password='{conf['password']}' sslmode='{conf['sslmode']}'"
        # print connection string we will use to connect
        #print("Connecting to database\n    ->%s" % (conn_string))
        # get a connection, if a connect cannot be made an exception will be raised here
        try:
            conn = psycopg2.connect(conn_string)
        except Exception as e:
            print(e)
            sys.exit
        #conn.set_isolation_level(0)
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        cursor = conn.cursor()
        dnow = datetime.datetime.now()
        log.info(f'{dnow.strftime("%Y-%m-%d %H:%M:%S")} - Connected to {self.dbname}\n')
        #print(f'{dnow.strftime("%Y-%m-%d %H:%M:%S")} - Connected to {self.dbname}\n')
        return conn,cursor