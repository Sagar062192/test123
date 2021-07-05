import re
import gzip
import os
import ast
import json
import pandas as pd


file = open("/home/vivek/Downloads/verbs_and_routes.txt")

line = file.read()
file.close()
test = re.split("(?<!\\\\)--", line)
test1 = [x.strip() for x in test]
lst_lines = [x for x in test1 if x != '']

data = []

for i in lst_lines:
    text = "".join(i.split())
    result = re.search(r"src/main/perl/lib/SIS/WS/(.*)Routes.pm.in-", text).group(1)
    verb = re.search(r"'([A-Za-z0-9_\./\\-]*)'", text).group(1)
    uri = re.search("pattern=>'(.*)',", text).group(1)
    pa = "/ping/(.*)"
    dict_data = {
        "resorce": result.replace("/",""),
        "verb": verb,
        "uri": uri,
    }
    data.append(dict_data)

patterns = []
for item in data:
    uri = item['uri']
    splitted_uri = uri.split('/')
    lst_uri_split = []
    for i in uri.split("/"):
        if ':' in i:
            if 'id' in i:
                i = re.sub(':(.*)', '[0-9]+', i)
            else:
                i = re.sub(':(.*)', '(.*)', i)
        lst_uri_split.append(i)
    patterns.append(item['verb']+' '+('/').join(lst_uri_split))

lst_post_urls = [i for i in patterns if i.split(" ")[0] == 'POST']
lst_patch_urls = [i for i in patterns if i.split(" ")[0] == 'PATCH']
print (lst_patch_urls)
lst_delete_urls = [i for i in patterns if i.split(" ")[0] == 'DELETE']

log_line = []
for i in [r'/home/vivek/Desktop/bansi_work/trace3.txt', r'/home/vivek/Desktop/bansi_work/trace4.txt']:
    fileLog = open(i)
    log = fileLog.readlines()
    fileLog.close()
    log_line.extend(log)

match_from_log = []
lst_post_url = []
for pattern in lst_post_urls:
    lst_data = []
    for i, item in enumerate(log_line):
        x_api_version = ""
        body_data = ""
        status_data = ""

        if re.search(pattern + " HTTP", item):
            # body_data = status_data = ''
            ip = item.split(':')[0]
            to_ip = item.split(':')[0].split('-')[0]
            from_ip = item.split(':')[0].split('-')[1]
            for p, x in enumerate(log_line[i + 1:]):
                if 'X-Api-Version' in x:
                    x_api_version = x.split(':')[-1].replace("", '').replace("\n", '')
                    break
            if pattern + x_api_version not in lst_post_url:
                lst_post_url.append(pattern + x_api_version)
            else:
                break
            for q, y in enumerate(log_line[i + 1:]):
                if ip in y:
                    if any(ext in y for ext in ['GET', 'POST', 'PATCH', 'DELETE']):
                        continue
                    pt = re.search(ip + ":(.*)", y)
                    body_data = pt.group(1).replace('"', "'") if pt else ""
                    break
            for yy in log_line[i+1:]:
                if from_ip + '-' + to_ip in yy:
                    status_data = yy.split(': ')[-1].replace("\n", '')
                    break
            if not body_data:
                for q, y in enumerate(log_line[i+1:]):
                    if y[0] == '{':
                        body_data = y
                        break

            lst_data.append({
                'x_api_version': x_api_version,
                'to_ip': item.split(':')[0].split('-')[0],
                'from_ip': item.split(':')[0].split('-')[1],
                'method': "POST",
                'url': item.split(" ")[2],
                'body_data': body_data,
                'status': status_data,
            })

    match_from_log.extend(lst_data)

# print final post data to file
df_post = pd.DataFrame(match_from_log)
df_post.to_csv('log_data_post.csv', index=False)

match_from_log_patch = []
lst_post_url = []
for pattern in lst_patch_urls:
    lst_data = []
    for i, item in enumerate(log_line):
        x_api_version = ""
        body_data = ""
        status_data = ""

        if re.search(pattern + " HTTP", item):
            # body_data = status_data = ''
            ip = item.split(':')[0]
            to_ip = item.split(':')[0].split('-')[0]
            from_ip = item.split(':')[0].split('-')[1]
            for p, x in enumerate(log_line[i + 1:]):
                if 'X-Api-Version' in x:
                    x_api_version = x.split(':')[-1].replace("", '').replace("\n", '')
                    break
            if pattern + x_api_version not in lst_post_url:
                lst_post_url.append(pattern + x_api_version)
            else:
                break
            for q, y in enumerate(log_line[i + 1:]):
                if ip in y:
                    if any(ext in y for ext in ['GET', 'POST', 'PATCH', 'DELETE']):
                        continue
                    pt = re.search(ip + ":(.*)", y)
                    body_data = pt.group(1).replace('"', "'") if pt else ""
                    break
            for yy in log_line[i+1:]:
                if from_ip + '-' + to_ip in yy:
                    status_data = yy.split(': ')[-1].replace("\n", '')
                    break
            if not body_data:
                for q, y in enumerate(log_line[i+1:]):
                    if y[0] == '{':
                        body_data = y
                        print ("ok44444444444444")
                        break

            lst_data.append({
                'x_api_version': x_api_version,
                'to_ip': item.split(':')[0].split('-')[0],
                'from_ip': item.split(':')[0].split('-')[1],
                'method': "PATCH",
                'url': item.split(" ")[2],
                'body_data': body_data,
                'status': status_data,
            })

    match_from_log_patch.extend(lst_data)

df_patch = pd.DataFrame(match_from_log_patch)
df_patch.to_csv('log_data_patch.csv', index=False)

# delete data to csv
match_from_log_delete = []
lst_post_url = []
for pattern in lst_delete_urls:
    lst_data = []
    for i, item in enumerate(log_line):
        x_api_version = ""
        body_data = ""
        status_data = ""

        if re.search(pattern + " HTTP", item):
            ip = item.split(':')[0]
            to_ip = item.split(':')[0].split('-')[0]
            from_ip = item.split(':')[0].split('-')[1]
            for p, x in enumerate(log_line[i + 1:]):
                if 'X-Api-Version' in x:
                    x_api_version = x.split(':')[-1].replace("", '').replace("\n", '')
                    break
            if pattern + x_api_version not in lst_post_url:
                lst_post_url.append(pattern + x_api_version)
            else:
                break
            for q, y in enumerate(log_line[i + 1:]):
                if ip in y:
                    if any(ext in y for ext in ['GET', 'POST', 'PATCH', 'DELETE']):
                        continue
                    pt = re.search(ip + ":(.*)", y)
                    body_data = pt.group(1).replace('"', "'") if pt else ""
                    break
            for yy in log_line[i + 1:]:
                if from_ip + '-' + to_ip in yy:
                    status_data = yy.split(': ')[-1].replace("\n", '')
                    break
            if not body_data:
                for q, y in enumerate(log_line[i + 1:]):
                    if y[0] == '{':
                        body_data = y
                        break

            lst_data.append({
                'x_api_version': x_api_version,
                'to_ip': item.split(':')[0].split('-')[0],
                'from_ip': item.split(':')[0].split('-')[1],
                'method': "DELETE",
                'url': item.split(" ")[2],
                'body_data': body_data,
                'status': status_data,
            })

    match_from_log_patch.extend(lst_data)

df_del = pd.DataFrame(match_from_log_delete)
df_del.to_csv('log_data_delete.csv', index=False)