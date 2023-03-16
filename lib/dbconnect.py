import os
import uuid

import MySQLdb as mysqldb

# get database details
database = "gystdb"
host = "localhost"
port = ""
user = "root"
password = ""

def connect_db(user, password, database):
    db = mysqldb.connect(user=user,password=password, database=database)
    return db

def exe_query(db, query):
    c = db.cursor()
    c.execute(query)
    return c.fetchall()

def get_columns(db, table):
    ins = db.cursor()
    getColNamesStmt = "describe " + table
    ins.execute(getColNamesStmt)
    print(ins.fetchall())

def getApiKey(user, password, dbname):
    api_key = None
    db_instance = connect_db(user, password, dbname)
    if db_instance is not None:
        api_key = str(uuid.uuid4())

    return api_key
