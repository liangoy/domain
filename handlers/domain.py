from hashlib import md5
from hashlib import sha1
import time
import requests
import grequests
import json

agent_id = '6'
public_key = '10COM_DMS_PRODUCTION'
password = 'sqsm1234'


def _get_headers(agent_id=agent_id, password=password, public_key=public_key):
    password_md5 = md5(password.encode()).hexdigest()
    timestamp = str(int(time.time()))
    s = password_md5 + '.' + agent_id + '.' + public_key + '.' + timestamp
    signature = sha1(s.encode()).hexdigest()
    headers = {
        'Accept': 'application/json',
        'agent-id': agent_id,
        'timestamp': timestamp,
        'signature': signature
    }
    return headers


def get_domain_status(domains):
    domains = list({i for i in domains.split(',') if i})
    info, cnt = [], 0
    while domains and cnt < 2:
        start_len = len(domains)
        tasks = [grequests.get('http://dms.test.com/api/v1/agent/domain/check?keyword=' + i, headers=_get_headers(),
                               timeout=6) for i in domains]
        data = zip(domains, grequests.map(tasks))
        domains = []
        for i in data:
            if i[1] and i[1].status_code < 400:
                content = json.loads(i[1]['comtent'].decode())
                info.append({'domain': i[0], 'status': str(content['in_use']), 'update_time': str(int(time.time()))})
            else:
                domains.append(i[0])
        end_len = len(domains)
        if start_len == end_len:
            cnt += 1
    for i in domains:
        info.append({'domain': i, 'status': 0, 'update_time': '0' * 10})
    return info


if __name__ == '__main__':
    print(_get_headers())
    print(requests.get('http://dms.10.com/api/v1/agent/domain/check?keyword=10.com', headers=_get_headers(),
                       timeout=6).status_code)
    print(requests.get('http://dms.10.com/api/v1/agent/domain/check?keyword=10.com', headers=_get_headers()).json())
    print(get_domain_status('10.com,20.com,30.com'))
