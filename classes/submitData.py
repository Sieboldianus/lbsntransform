# -*- coding: utf-8 -*-

import psycopg2
from decimal import Decimal
from classes.helperFunctions import helperFunctions
from classes.helperFunctions import lbsnRecordDicts as lbsnRecordDicts
from lbsnstructure.Structure_pb2 import *
from lbsnstructure.external.timestamp_pb2 import Timestamp
import logging 

class lbsnDB():  
    def submitLBSNRecord(record):      