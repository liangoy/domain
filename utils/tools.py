from hashlib import md5
from hashlib import sha1
import time
import json
import pymongo
import time
import requests

agent_id = '6'
public_key = '10COM_DMS_PRODUCTION'
password = 'sqsm1234'

client = pymongo.MongoClient('192.168.199.9')
db_register_status = client.domain.register_status
db_contact_template=client.contact_template


def _get_headers(agent_id=agent_id, password=password, public_key=public_key):
    password_md5 = md5(password.encode()).hexdigest()
    timestamp = str(int(time.time()))
    s = password_md5 + '.' + agent_id + '.' + public_key + '.' + timestamp
    signature = sha1(s.encode()).hexdigest()
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'multipart/form-data',
        'agent-id': agent_id,
        'timestamp': timestamp,
        'signature': signature
    }
    return headers

if __name__=='__main__':
    print(_get_headers())