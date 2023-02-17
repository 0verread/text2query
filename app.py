#!./venv/bin/python
import json
import openai
import os

import subprocess
import sys

openai.api_key = os.environ['OPENAI_API_KEY']

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
    print(result.stdout)
    return result.stdout


if __name__ == "__main__":
  provided_prompt_str = sys.argv[1]
  final_prompt = "{}{}".format('A query to get', provided_prompt_str)
  response = makeit(final_prompt)
  query = response.replace("\n", " ")
  input_file = "assets/employees.csv"
  run_csvsql_query(input_file, query)
  
