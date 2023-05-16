import http.client
import urllib.parse
import sys

from libstrava import edgestest, gradtest, pointstest

HOST = '127.0.0.1'
PORT = 8080

def request(content):
    conn = http.client.HTTPConnection("localhost", PORT)

    headers = { 'content-type': 'application/x-www-form-urlencoded', }
    body = 'full_data=' + urllib.parse.quote(content)
    conn.request('POST', '/api/v1', body=body, headers=headers)

    r = conn.getresponse()
    return r.read().decode()

def main():
    content = """get_init
    """
    print(request(content))
    for file in sys.argv[1:]:
        if file == "edges" or file == "edges.py":
            edgestest()
        elif file == "fast_gradient_decent" or file == "fast_gradient_decent.py" or file == "gradient_decent" or file == "gradient_decent.py":
            gradtest()
        elif file == "points" or file == "points.py":
            pointstest()
        else:
            print(f"not found: {file}")

if __name__ == "__main__":
    main()
