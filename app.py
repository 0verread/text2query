#!./venv/bin/python
import json
import openai
import os

import subprocess
import sys

openai.api_key = os.environ['OPENAI_API_KEY']

# make prompt more dynamic
# show output in a table like UI

def makeit(prompt):
  response = openai.Completion.create(
    # model="code-davinci-002",
    model="davinci-codex",
    # prompt=prompt,
    # prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to get employees who salary is greater than 25000 \nSELECT",
    prompt="### Postgres SQL tables, with their properties:\n#\n# employees(EMPLOYEE_ID,FIRST_NAME,LAST_NAME,EMAIL,PHONE_NUMBER,HIRE_DATE,JOB_ID,SALARY,COMMISSION_PCT,MANAGER_ID,DEPARTMENT_ID)\n#\n### {} \nSELECT".format(prompt),
    temperature=0.5,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["#", ";"]
  )
  # print(response.choices[0])
  sqlRes = response.choices[0].text
  new_sql_q = sqlRes.replace("\n", " ")
  final_sql_q = '{}{}'.format('SELECT',new_sql_q)
  args  = ["--query", f"{final_sql_q}", "assets/employees.csv"]
  res = subprocess.run(["csvsql"] + args, capture_output=True, text=True)
  print(res.stdout)
  print(res.stderr)


def run_csvsql_query():




provided_prompt_str = sys.argv[1]
makeit("{}{}".format('A query to get',provided_prompt_str))





















# from gpt import GPT
# from gpt import Example

# gpt = GPT(engine="davinci",
#           temperature=0.5,
#           max_tokens=100)

# gpt.add_example(Example('Fetch unique values of DEPARTMENT from Worker table.', 
#                         'Select distinct DEPARTMENT from Worker;'))
# gpt.add_example(Example('Print the first three characters of FIRST_NAME from Worker table.', 
#                         'Select substring(FIRST_NAME,1,3) from Worker;'))
# gpt.add_example(Example("Find the position of the alphabet ('a') in the first name column 'Amitabh' from Worker table.", 
#                         "Select INSTR(FIRST_NAME, BINARY'a') from Worker where FIRST_NAME = 'Amitabh';"))
# gpt.add_example(Example("Print the FIRST_NAME from Worker table after replacing 'a' with 'A'.", 
#                         "Select CONCAT(FIRST_NAME, ' ', LAST_NAME) AS 'COMPLETE_NAME' from Worker;"))
# gpt.add_example(Example("Display the second highest salary from the Worker table.", 
#                         "Select max(Salary) from Worker where Salary not in (Select max(Salary) from Worker);"))
# gpt.add_example(Example("Display the highest salary from the Worker table.", 
#                         "Select max(Salary) from Worker;"))
# gpt.add_example(Example("Fetch the count of employees working in the department Admin.", 
#                         "SELECT COUNT(*) FROM worker WHERE DEPARTMENT = 'Admin';"))
# gpt.add_example(Example("Get all details of the Workers whose SALARY lies between 100000 and 500000.", 
#                         "Select * from Worker where SALARY between 100000 and 500000;"))
# gpt.add_example(Example("Get Salary details of the Workers", 
#                         "Select Salary from Worker"))


# prompt = "Display the lowest salary from the Worker table."
# output = gpt.submit_request(prompt)
# output.choices[0].text