#!./venv/bin/python
import json
import openai
import os

import subprocess
import sys

from flask import Flask, request, jsonify
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
from flask_mysqldb import MySQL

from lib.dbconnect import connect_db, exe_query, getApiKey 



app = Flask(__name__)
# bolt_app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

openai.api_key = os.environ['OPENAI_API_KEY']

db_ins  = None


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


@app.route('/auth', methods=['POST'])
def db_auth():
  response = None
  if not request.json : 
    response.status = "400"
    response.data = "No data is provided"

  dbpassword = request.json['dbpassword']
  dbuser = request.json['dbuser']
  dbname = request.json['dbname']
  name = request.json['name']

  try:
    global db_ins
    api_key = getApiKey(name, dbuser, dbpassword, dbname)
    if api_key is not None:
      response = jsonify({"status": "200", "data": "Connection established", "API_Key": api_key})
    else:
      response = jsonify({"status": "400", "data": "Could not create API key. ", "API_Key": api_key})
  except Exception as e:
    print(e)
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

  # TODO: check if API key is valid
  if api_key:
    res = exe_query(api_key, query)
    print("res:" )
    print(res)
  else:  
    res = "API key is not provided"
  response = jsonify({"status": "200", "data": res})
  return response

  
@app.errorhandler(404)
def not_found(error):
  return jsonify({'error': 'Not found'})

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=3030, debug=False)
  
