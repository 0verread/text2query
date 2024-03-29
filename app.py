#!./venv/bin/python3

import subprocess

from flask import Flask, request, jsonify
# For future use
# from flask_restful import Resource, Api

app = Flask(__name__)

db_ins  = None

def run_csvsql_query(input_file, query):
    final_sql_query = '{}{}'.format('SELECT', query)
    args = ["--query", f"{final_sql_query}", input_file]
    result = subprocess.run(["csvsql"] + args, capture_output=True, text=True)
    if result.returncode != 0:
      print(f'Error running query:{result.stderr}')
      return None
    else:
      return result.stdout


@app.route('/')
def home():
  return jsonify({"status": "200", "data": 'Orgate AI api'})

@app.route('/auth', methods=['POST'])
def db_auth():
  response = None
  if not request.json :
    response.status = "400"
    response.data = "No data provided"

  name = request.json['name']
  try:
    api_key = lib.dbconnect.getApiKey(name)
    if api_key is not None:
      response = jsonify({"status": "200", "data": "Connection established", "API_Key": api_key})
    else:
      response = jsonify({"status": "400", "data": "Could not create API key. ", "API_Key": api_key})
  except Exception as e:
    response = jsonify({"status": "400", "data": "Connection could not be established"})
  return response

@app.route('/config', methods=['POST'])
def config():
  response = None

  if not request.json :
    response.status = "400"
    response.data = "No data provided"

  allowed_tables = request.json['tables']
  api_key = request.json.get('api_key')
  db_config = request.json['db_config']

  table_schema = lib.dbconnect.get_table_schema(db_config, api_key, allowed_tables)
  file_name = lib.dbconnect.save_schema_file(api_key, table_schema)

  if file_name:
    response = jsonify({"status": "200", "data": "Success"})
  else:
    response = jsonify({"status": "200", "data": "Something went wrong."})

  return response

""" Right now, you have to pass SQL query to test this API
    TODO: It takes query in natural lang, retrun result"""

@app.route('/query', methods=['POST'])
def query():
  global db_ins
  response = None
  api_key = request.json.get('api_key')
  query = request.json.get('query')
  db_schema = request.json.get('db_schema')
  # db_config = request.json.get('db_config')

  # TODO: check if API key is valid
  if api_key:
    # res = lib.dbconnect.exe_query(api_key, query)
    res  = lib.dbconnect.get_sql_query(api_key, query, db_schema)
  else:
    res = "API key is not provided"
  response = jsonify({"status": "200", "data": res})
  return response

@app.route('/config', methods=['GET', 'POST'])
def dbConfig():
  response = None
  api_key = request.json.get('api_key')



@app.errorhandler(404)
def not_found(error):
  return jsonify({'error': 'Route Not found'})

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=3000, debug=False)


