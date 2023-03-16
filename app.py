#!./venv/bin/python
import json
import openai
import os

import subprocess
import sys
import psycopg2

from flask import Flask, request, jsonify
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
from flask_mysqldb import MySQL

# sys.path.insert(0, '/Users/subhajit/workspace/text2query/lib/')
from lib.dbconnect import connect_db, exe_query 



app = Flask(__name__)
bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

openai.api_key = os.environ['OPENAI_API_KEY']

db_ins  = None

# database variables
# database = os.environ['DATABASE']
# host = os.environ['HOST']
# port = os.environ['PORT']
# user = os.environ['USER']
# password = os.environ['PASSWORD']

# make prompt more dynamic
  #  - Get columns using pandas
  #  - 
# show output in a table like UI

def makeit(prompt):
  response = openai.Completion.create(
    # model="code-davinci-002",
    model="davinci-codex",
    # prompt=prompt,
    # prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to get employees who salary is greater than 25000 \nSELECT",
    # TODO: break this prompt string
    prompt="### Postgres SQL tables, with their properties:\n#\n# employees(EMPLOYEE_ID,FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUMBER,HIRE_DATE,JOB_ID,SALARY,COMMISSION_PCT,MANAGER_ID,DEPARTMENT_ID)\n#\n### {} \nSELECT".format(prompt),
    temperature=0.5,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["#", ";"]
  )
  return response.choices[0].text


def run_csvsql_query(input_file, query):
  final_sql_query = '{}{}'.format('SELECT', query)
  args = ["--query", f"{final_sql_query}", input_file]
  result = subprocess.run(["csvsql"] + args, capture_output=True, text=True)
  if result.returncode != 0:
    print(f'Error running query:{result.stderr}')
    return None
  else:
    # print(result.stdout)
    return result.stdout


def db_connnection():
  conn = psycopg2.connect(database=database,
                          host=host,
                          user=user,
                          password=password,
                          port=port)

  cursor = conn.cursor()
  cursor.execute("SELECT * FROM employees")
  print(cursor.fetchall())
  # print('coming here')


# @app.route('/test', methods=['POST', 'GET'])
# def final():
#   password = "newpassword"
#   user = "root"
#   database = "gystdb"
#   db_ins = connect_db(user, password, database)
#   res = exe_query(db_ins, "Select * from todolist")
#   print(type(res))
#   print(jsonify(res))
#   # dbconnect.get_columns(db_ins, "todolist")
#   return {"status": "200", "data": res}

# @app.route('/auth', methods=['POST'])
def db_auth(dbuser, dbpassword, dbname):
  response = None
  # if not request.json : 
  #   response.status = "400"
  #   response.data = "No data is provided"

  app.config['MYSQL_USER'] = dbuser
  app.config['MYSQL_PASSWORD'] = dbpassword
  app.config['MYSQL_DB'] = dbname
  try:
    global db_ins
    db_ins = connect_db(dbuser, dbpassword, dbname)
    response = jsonify({"status": "200", "data": "Connection established"})
  except Exception as e:
    response = jsonify({"status": "400", "data": "Connection could not be established", "error": e})
  return response



""" Right now, you have to pass SQL query to test this API
    TODO: It takes query in natural lang, retrun result"""

@app.route('/query', methods=['POST'])
def query():
  global db_ins
  response = None
  query = request.json['query']

  dbpassword = request.json['dbpassword']
  dbuser = request.json['dbuser']
  dbname = request.json['dbname']

  db_auth_status = db_auth(dbuser, dbpassword, dbname)
  print(db_auth_status)
  
  if db_ins is None:
    response = jsonify({"status": "400", "data": "DB connection is failed"})
    return response
  res = exe_query(db_ins, query)
  response = jsonify({"status": "200", "data": res})
  return response

  
@app.errorhandler(404)
def not_found(error):
  return jsonify({'error': 'Not found'})

# @bolt_app.message("friday")
# def greetings(payload: dict, say: Say):
#   user: str = payload.get("user")
#   say(f"Hello sir")


# @bolt_app.command("/friday")
# def real_do(ack, respond, command):
#   ack()
#   question = command['text']
#   final_prompt = "{}{}".format('A query to get', question)
#   response = makeit(final_prompt)
#   query = response.replace("\n", " ")
#   input_file = "assets/employees.csv"
#   ans = run_csvsql_query(input_file, query)
#   res = "Your query: {}\n".format(question)
#   final_res = "{}Answer:\n{}".format(res, ans)
#   respond(final_res)



# handler = SlackRequestHandler(bolt_app)

# @app.route("/friday/events", methods=['POST'])
# def slack_events():
#   return handler.handle(request)



if __name__ == "__main__":
  # provided_prompt_str = sys.argv[1]
  # db_connnection()
  # final_prompt = "{}{}".format('A query to get', provided_prompt_str)
  # response = makeit(final_prompt)
  # query = response.replace("\n", " ")
  # input_file = "assets/employees.csv"
  # run_csvsql_query(input_file, query)
  app.run(host='0.0.0.0', port=3030, debug=False)
  
