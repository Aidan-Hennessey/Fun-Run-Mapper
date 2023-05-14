import http.client
import urllib.parse

HOST = 'sky.jason.cash'
PORT = 8080

def request(content):
    conn = http.client.HTTPSConnection(HOST, PORT)

    headers = { 'content-type': 'application/x-www-form-urlencoded', }
    body = 'full_data=' + urllib.parse.quote(content)
    conn.request('POST', '/', body=body, headers=headers)

    r = conn.getresponse()
    return r.read().decode()

def main():
    content = """hello
    80948 90328 4098 2903
    39048 20398 40392
    483209 493028 403928 49320 
    9038 409832 09423 4302
    """
    print(request(content))

if __name__ == "__main__":
    main()
