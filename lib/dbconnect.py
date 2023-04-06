import os
import uuid
import json
import openai
import datetime
import string, random

import MySQLdb as mysqldb
import psycopg2


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


# Support of postgresql
def psqldb_connnection(database, user, password, host=None, port=None):
  conn = psycopg2.connect(database=database,
                          host=host,
                          user=user,
                          password=password,
                          port=port)

  cursor = conn.cursor()
  return conn


# supoort of mysql DB
def mysql_connection(user, password, dbname, host=None, port=None):
    conn = mysqldb.connect(user=user, password=password, database=dbname)
    return conn

# plannetscale DB 
def connect_db():
    # database = "gystdb"
    # host = "localhost"
    # port = ""
    # user = "root"
    # password = "newpassword"

    host = os.getenv("HOST")
    user = os.getenv("DBUSER")
    passwd = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    ssl_mode = "VERIFY_IDENTITY"
    ssl = {
        "ca": "/etc/ssl/cert.pem"
    }

    db = mysqldb.connect(host=host, user=user, password=passwd, database=database, ssl_mode=ssl_mode, ssl=ssl)
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
        schema = {column[0]: column[1] for column in columns}
        table_schemas[table] = schema
    return table_schemas

# Create prompt
def get_prompt(query, schema_file):
    # Employee(id, name, department_id)\n# Department(id, name, address)\n#
    table_strings = []
    file = open(schema_file, 'r')
    schema = json.loads(file.read())
    for table_name, table_info in schema.items():
        columns = [f"{col_name}" for col_name, col_type in table_info.items()]
        table_string = f"{table_name}({', '.join(columns)})"
        table_strings.append(table_string)
    schema_part = r'\n# '.join(table_strings)
    return schema_part


def exe_query(api_key, query):
    db_config = db_config_by_apikey(api_key)

    # Get DB config
    db_con = db_config[0][1:4]
    dbname = db_con[1]
    user = db_con[2]
    # password = db_con[3]
    # making DB connection: test postgres
    db = psqldb_connnection(dbname, user, '')
    c = db.cursor()
    columns_schema = get_table_schema(c, ['employees','departments','titles', 'dept_manager', 'salaries', 'works_in'])

    # Get the query ready using OpenAI api
    text_q = query
    final_prompt = "{}{}".format('A query to get ', text_q)
    
    # Save it as a JSON file
    file_name = api_key + '.json'
    with open(file_name, 'w') as file:
        json.dump(columns_schema, file)
    table_schemas_str = get_prompt(query, file_name) + ''
    # print(table_schemas_str, type(table_schemas_str))
    sql_stmt = makeit(table_schemas_str, final_prompt)
    final_sql_q = sql_stmt.replace("\\n", " ").replace("\n", " ")
    # execute the sql stmt
    # final_sql_q = getSqlStmt(query)
    c.execute('select ' + final_sql_q)
    return c.fetchall()

def get_columns(db, table):
    ins = db.cursor()
    getColNamesStmt = "describe " + table
    ins.execute(getColNamesStmt)
    print(ins.fetchall())

def getId():
    size = 6
    chars= string.ascii_uppercase + string.digits
    id  = ''.join(random.choices(chars, k=size))
    return id

def getApiKey(name, dbuser, dbpassword, dbname):
    api_key = None
    db_instance = connect_db()
    id = getId()
    if db_instance is not None:
        api_key = 'orai' + str(uuid.uuid4())
        curr = db_instance.cursor()
        now = datetime.datetime.now()
        curr.execute('INSERT INTO customers (id, name, dbname, dbuser, dbpassword, apikey, totalapicall, created_at) values (%s, %s, %s, %s, %s, %s, %s, %s)', 
                     (id, name, dbname, dbuser, dbpassword, api_key, 0, now))
        db_instance.commit()
    return api_key

def db_config_by_apikey(api_key):
    db_instance = connect_db()
    curr = db_instance.cursor()
    if api_key:
        curr.execute('SELECT * FROM customers WHERE apikey = %s', [api_key])
        return curr.fetchall()
    return None



