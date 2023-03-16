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

from lib.dbconnect import connect_db, exe_query, getApiKey 



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

@app.route('/auth', methods=['POST'])
def db_auth():
  response = None
  if not request.json : 
    response.status = "400"
    response.data = "No data is provided"

  dbpassword = request.json['dbpassword']
  dbuser = request.json['dbuser']
  dbname = request.json['dbname']

  try:
    global db_ins
    api_key = getApiKey(dbuser, dbpassword, dbname)
    if api_key is not None:
      response = jsonify({"status": "200", "data": "Connection established", "API_Key": api_key})
    else:
      response = jsonify({"status": "400", "data": "Could not create API key. ", "API_Key": api_key})
  except Exception as e:
    response = jsonify({"status": "400", "data": "Connection could not be established"})
  return response


""" Right now, you have to pass SQL query to test this API
    TODO: It takes query in natural lang, retrun result"""
@app.route('/query', methods=['POST'])
def query():
  global db_ins
  response = None
  api_key = request.json.get('api_key')
  query = request.json.get('query')

  if api_key:
    res = exe_query(db_ins, query)
  else:  
    res = "API key is not provided"
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
  
