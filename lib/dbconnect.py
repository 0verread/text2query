import os
import uuid

import MySQLdb as mysqldb

# get database details
database = "gystdb"
host = "localhost"
port = ""
user = "root"
password = "newpassword"

def connect_db():
    db = mysqldb.connect(user=user,password=password, database=database)
    return db

def connect_cust_db(user, password, dbname):
    cust_db = mysqldb.connect()

def exe_query(api_key, query):
    db_config = db_config_by_apikey(api_key)
    print(db_config)
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
    db_instance = connect_db()
    if db_instance is not None:
        api_key = str(uuid.uuid4())
        curr = db_instance.cursor()
        curr.execute('INSERT INTO dbapikey (dbname, user, password, apikey) values (%s, %s, %s, %s)', (dbname, user, password, api_key))
        db_instance.commit()
    return api_key

def db_config_by_apikey(api_key):
    db_instance = connect_db()
    curr = db_instance.cursor()
    if api_key:
        # print(stmt)
        curr.execute("SELECT * FROM dbapikey WHERE apikey = {}".format(api_key))
        return curr.fetchall()
    return None



