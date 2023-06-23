import uuid4
import string, random
import datetime

import bcrypt

API_KEY_PREFIX = 'orai-'
ID_SIZE = 6

def getId(prefix):
    chars = string.ascii_uppercase + string.digits
    id  = prefix + ''.join(random.choices(chars, k=ID_SIZE))
    return id

def getHashedPass(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))

def get_file_name(api_key, dbname):
    return f'{api_key}_{dbname}.json'

def get_api_key():
    return API_KEY_PREFIX+ str(uuid.uuid4())

def get_dbconfig(dbname, dbuser, dbpassword, host):
    hashed_pass = getHashedPass(dbpassword)
    config = {"dbuser": dbuser, "dbpassword": hashed_pass.decode('utf-8'), "host": host}
    return json.dumps({dbname : config})
