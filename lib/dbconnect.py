import os

import MySQLdb as mysqldb

# get database details
database = "gystdb"
host = "localhost"
port = ""
user = "root"
password = "newpassword"

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

# c=db.cursor()
# max_price=5
# c.execute("""SELECT * from todolist""")
# print(c.fetchall())