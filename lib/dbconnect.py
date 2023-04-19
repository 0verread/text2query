import os
import uuid
import json
import openai
import datetime
import string, random

import MySQLdb as mysqldb
import psycopg2
import bcrypt


from dotenv import load_dotenv

load_dotenv()

# get database details
def makeit(table_schema, prompt):
  test = table_schema + r"\n#\n### " +  prompt + r" \nSELECT"
  prompt1= r"### Postgres SQL tables, with their properties:\n#\n# " + test
  response = openai.Completion.create(
    model="text-davinci-003",
    # prompt=prompt,
    # prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to get employees who salary is greater than 25000 \nSELECT",
    # TODO: break this prompt string
    # prompt= "### Postgres SQL tables, with their properties:\n#\n# employees(emp_no, birth_date, first_name, last_name, hire_date)\n#\n### {} \nSELECT".format(prompt),
    prompt = prompt1,
    temperature=0.5,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["#", ";"]
  )
  return response.choices[0].text

# --------------------------------------------------------------------------------------- #
""" 
All this functions are designed to create a connection with Customer DB.
Right now, we have support for PostgresQL and MySQL database.
"""

# Support of postgresql
def psqldb_connnection(user, password, dbname, host=None, port=None):
  conn = psycopg2.connect(database=dbname,
                          host=host,
                          user=user,
                          password=password,
                          port=port)

  return conn


# supoort of mysql DB
def mysql_connection(user, password, dbname, host=None, port=None):
    conn = mysqldb.connect(user=user, password=password, database=dbname, host=host)
    return conn

# Customer DB connector controller 
def connect_cust_db(dbtype, db_config):
    dbname, user, password, host = getConfig(db_config)
    if dbtype == "MySQL":
        return mysql_connection(user, password, dbname, host)
    elif dbtype == "PostgresSQL":
        return psqldb_connnection(user, password, dbname, host)
    return None

# --------------------------------------------------------------------------- #

def db_config_by_apikey(api_key):
    db_instance = connect_db()
    curr = db_instance.cursor()
    if api_key:
        curr.execute('SELECT dbconfig FROM customers WHERE apikey = %s', [api_key])
        return curr.fetchall()
    return None


def get_dbconn_by_apikey(db_type, api_key):
    db_config = list(zip(db_config_by_apikey(api_key)))
    db_config_str = db_config[0][0][0]
    db_config_dict = json.loads(db_config_str)

    # Get DB config
    # db_con = db_config[0][1:4]
    dbname = list(db_config_dict.keys())[0]
    config = list(db_config_dict.values())[0]

    host, user, password = getConfig(config.values()) 

    # Check DB type and make conn accordingly
    if db_type.casefold() == "mysql":
        db = mysql_connection()
    elif db_type.casefold() == "postgresql":
        # For localhost DB
        db = psqldb_connnection(user, '', dbname)
        # db  = psqldb_connnection(user, password, dbname, host)
    # making DB connection: test postgres
    return db


# -------------------------------------------------------------------------------


"""
This are lib functions. pretty generic
TODO: move to a separate file
"""

def getId(prefix):
    size = 6
    chars= string.ascii_uppercase + string.digits
    id  = prefix + ''.join(random.choices(chars, k=size))
    return id

def getHashedPass(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))

def get_file_name(api_key, dbname):
    return f'{api_key}_{dbname}.json'

def get_api_key():
    return 'orai-' + str(uuid.uuid4())

def get_dbconfig(dbname, dbuser, dbpassword, host):
    hashed_pass = getHashedPass(dbpassword)
    config = {"dbuser": dbuser, "dbpassword": hashed_pass.decode('utf-8'), "host": host}
    return json.dumps({dbname : config})

# ---------------------------------------------------------------------------------- #

def getConfig(db_config):
    config = list(db_config)
    return config[0], config[1], config[2]

# ------------------------------------------------------------------------------------ #

# plannetscale DB : Our prod DB
def connect_db():
    host = os.getenv("HOST")
    user = os.getenv("DBUSER")
    passwd = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    ssl_mode = "VERIFY_IDENTITY"
    ssl = {
        "ca": "/etc/pki/tls/certs/ca-bundle.crt"
    }

    db = mysqldb.connect(host=host, user=user, password=passwd, database=database)
    return db

def get_dbname_by_apikey(api_key):
    db_config = list(zip(db_config_by_apikey(api_key)))
    db_config_str = db_config[0][0][0]
    db_config_dict = json.loads(db_config_str)

    # Get DB config
    dbname = list(db_config_dict.keys())[0]
    return dbname


def save_schema_file(api_key, schema):
    # file_name = None

    # db_config = list(zip(db_config_by_apikey(api_key)))
    # db_config_str = db_config[0][0][0]
    # db_config_dict = json.loads(db_config_str)

    # Get DB Name
    dbname = schema.get('dbname')
    # Save it as a JSON file
    file_name = get_file_name(api_key, dbname)
    with open(file_name, 'w') as file:
        json.dump(schema, file)
    return file_name

# Get table schema
def get_table_schema(db_type, api_key, tables):
    conn = get_dbconn_by_apikey(db_type, api_key)
    dbname = get_dbname_by_apikey(api_key)
    curr = conn.cursor()
    table_schemas = {}
    for table in tables:
        curr.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}'")
        columns = curr.fetchall()
        schema = {column[0]: column[1] for column in columns}
        table_schemas[table] = schema
    return {"dbname":dbname, "dbtype": db_type, "schema": table_schemas}

# Create prompt
def get_prompt(query, schema_file):
    table_strings = []
    file = open(schema_file, 'r')
    schema = json.loads(file.read())
    table_schema = schema.get('schema')
    for table_name, table_info in table_schema.items():
        columns = [f"{col_name}" for col_name, col_type in table_info.items()]
        table_string = f"{table_name}({', '.join(columns)})"
        table_strings.append(table_string)
    schema_part = r'\n# '.join(table_strings)
    return schema_part


def exe_query(api_key, query):
    dbname = get_dbname_by_apikey(api_key)
    config_file_name = get_file_name(api_key, dbname)
    file = open(config_file_name, 'r')
    schema = json.loads(file.read())
    db_type = schema.get('dbtype')
    conn = get_dbconn_by_apikey(db_type, api_key)
    cur = conn.cursor()


    # TODO: tables name should be dynamic
    # columns_schema = get_table_schema(cur, ['employees','departments','titles', 'dept_manager', 'salaries', 'works_in'])

    # Get the query ready using OpenAI api
    text_q = query
    final_prompt = "{}{}".format('A query to get ', text_q)

    file_name = get_file_name(api_key, dbname)
    table_schemas_str = get_prompt(query, file_name) + ''
    sql_stmt = makeit(table_schemas_str, final_prompt)
    final_sql_q = sql_stmt.replace("\\n", " ").replace("\n", " ")
    cur.execute('select ' + final_sql_q)
    return cur.fetchall()

def get_columns(db, table):
    ins = db.cursor()
    getColNamesStmt = "describe " + table
    ins.execute(getColNamesStmt)
    print(ins.fetchall())

def getApiKey(name, dbuser, dbpassword, dbname, host=None):
    api_key = None
    # TODO: Shoudn't be connecting everytime making api call
    db_instance = connect_db()
    id = getId('org')
    if db_instance is not None:
        # TODO: check if config is right before creating API key
        api_key = get_api_key()
        curr = db_instance.cursor()
        dbconfig = get_dbconfig(dbname, dbuser, dbpassword, host)
        now = datetime.datetime.now()
        curr.execute('INSERT INTO customers (id, name, apikey, totalapicall, created_at, dbconfig) values (%s, %s, %s, %s, %s, %s)', 
                     (id, name, api_key, 0, now, dbconfig))
        db_instance.commit()
    return api_key



