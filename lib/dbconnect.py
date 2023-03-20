import os
import uuid
import json
import openai

import MySQLdb as mysqldb

# get database details
database = "gystdb"
host = "localhost"
port = ""
user = "root"
password = "newpassword"

def makeit(prompt):
  response = openai.Completion.create(
    # model="code-davinci-002",
    model="davinci-codex",
    # prompt=prompt,
    # prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to get employees who salary is greater than 25000 \nSELECT",
    # TODO: break this prompt string
    prompt="### Postgres SQL tables, with their properties:\n#\n# todolist(title, description, isDone)\n#\n### {} \nSELECT".format(prompt),
    temperature=0.5,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["#", ";"]
  )
  return response.choices[0].text

def connect_db():
    db = mysqldb.connect(user=user,password=password, database=database)
    return db

def connect_cust_db(user, password, dbname, host=None, port=None):
    cust_db = mysqldb.connect(user=user,password=password, database=dbname)
    return cust_db

def exe_query(api_key, query):
    db_config = db_config_by_apikey(api_key)

    # Get the query ready using OpenAI api
    text_q = query
    final_prompt = "{}{}".format('A query to get ', text_q)
    sql_stmt = makeit(final_prompt)
    print(final_prompt)
    final_sql_q = sql_stmt.replace("\n", " ")
    print(final_sql_q)
    # Get DB config
    db_con = db_config[0][1:4]
    dbname = db_con[0]
    user = db_con[1]
    password = db_con[2]

    # making DB connection
    db = connect_cust_db(user, password, dbname)
    c = db.cursor()

    # execute the sql stmt
    c.execute('SELECT' + final_sql_q)
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
        curr.execute('SELECT * FROM dbapikey WHERE apikey = %s', [api_key])
        return curr.fetchall()
    return None



