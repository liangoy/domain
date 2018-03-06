import grequests
import json
import time
from utils import tools


def get_register_status(domains, fast, store):
    domains = [i for i in domains.split(',') if i]
    if fast:
        lis = list(tools.db_register_status.find({'domain': {'$in': domains}}))
        for i in lis:
            ts = int(str(i.pop('_id'))[:8], 16)
            i['update_time'] = ts
        domains_in_db = {i['domain'] for i in lis}
        domains_not_find = set(domains) - domains_in_db
        for i in domains_not_find:
            lis.append({
                'domain': i,
                'update_time': '0' * 10,
                'status': '0'
            })
        return lis
    else:
        info, cnt = [], 0
        while domains and cnt < 2:
            start_len = len(domains)
            tasks = [
                grequests.get('http://dms.10.com/api/v1/agent/domain/check?keyword=' + i, headers=tools._get_headers(),
                              timeout=6) for i in domains]
            data = zip(domains, grequests.map(tasks))
            domains = []
            for i in data:
                if i[1] and i[1].status_code < 400:
                    content = json.loads(i[1]['comtent'].decode())
                    info.append(
                        {'domain': i[0], 'status': str(content['in_use']), 'update_time': str(int(time.time()))})
                else:
                    domains.append(i[0])
            end_len = len(domains)
            if start_len == end_len:
                cnt += 1
        if store:
            put_register_status([[i['domain'], i['status']] for i in info])
        for i in domains:
            info.append({'domain': i, 'status': '0', 'update_time': '0' * 10})
        return info


def put_register_status(domains_and_status):
    if not domains_and_status:
        return []
    dic = {i[0]: i[1] for i in domains_and_status}
    tools.db_register_status.delete_many({'domain': {'$in': list(dic.keys())}})
    tools.db_register_status.insert_many([{'domain': i, 'status': dic[i]} for i in dic])
    return list(dic.keys())


def delete_register_status(domains):
    domains = list({i for i in domains.split(',') if i})
    tools.db_register_status.delete_many({'domain': {'$in': domains}})
    return domains


if __name__ == '__main__':
    print(tools._get_headers())
