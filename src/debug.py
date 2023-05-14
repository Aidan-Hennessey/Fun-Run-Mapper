import http.client
import urllib.parse

content = """hello
80948 90328 4098 2903
39048 20398 40392
483209 493028 403928 49320 
9038 409832 09423 4302
"""

headers = {
    'content-type': 'application/x-www-form-urlencoded',
}

HOST = 'sky.jason.cash'
PORT = 8080

conn = http.client.HTTPSConnection(HOST, PORT)

body = 'full_data=' + urllib.parse.quote(content)
conn.request('POST', '/', body=body, headers=headers)
r = conn.getresponse()
print(r.read().decode())

