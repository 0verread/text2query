import os
import uuid
import json
import openai

import MySQLdb as mysqldb
import psycopg2

# get database details
def makeit(prompt):
  response = openai.Completion.create(
    # model="code-davinci-002",
    model="davinci-codex",
    # prompt=prompt,
    # prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to get employees who salary is greater than 25000 \nSELECT",
    # TODO: break this prompt string
    prompt="### Postgres SQL tables, with their properties:\n#\n# employees(emp_no, birth_date, first_name, last_name, hire_date)\n#\n### {} \nSELECT".format(prompt),
    temperature=0.5,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["#", ";"]
  )
  return response.choices[0].text


def psqldb_connnection(database, user, password, host=None, port=None):
  conn = psycopg2.connect(database=database,
                          host=host,
                          user=user,
                          password=password,
                          port=port)

  cursor = conn.cursor()
  # cursor.execute("SELECT * FROM employees limit 5")
  return conn

def connect_db():
    database = "gystdb"
    host = "localhost"
    port = ""
    user = "root"
    password = "newpassword"

    db = mysqldb.connect(user=user,password=password, database=database)
    return db

def connect_cust_db(user, password, dbname, host=None, port=None):
    cust_db = mysqldb.connect(user=user,password=password, database=dbname)
    return cust_db

# Get table schema
def get_table_schema(curr, tables):
    table_schemas = {}
    for table in tables:
        curr.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}'")
        columns = curr.fetchall()
        # print(columns)
        schema = {column[0]: column[1] for column in columns}
        table_schemas[table] = schema
    print(table_schemas)
    return table_schemas

def exe_query(api_key, query):
    db_config = db_config_by_apikey(api_key)

    # Get the query ready using OpenAI api
    text_q = query
    final_prompt = "{}{}".format('A query to get ', text_q)
    sql_stmt = makeit(final_prompt)
    final_sql_q = sql_stmt.replace("\n", " ")

    # Get DB config
    db_con = db_config[0][1:4]
    dbname = db_con[0]
    user = db_con[1]
    password = db_con[2]

    # making DB connection: test postgres
    db = psqldb_connnection(dbname, user, password)
    c = db.cursor()
    get_table_schema(c, ['employees','departments','titles'])
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



