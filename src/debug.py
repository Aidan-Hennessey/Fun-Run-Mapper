import http.client
import urllib.parse
import sys

from libstrava import edgestest, gradtest, pointstest

HOST = '127.0.0.1'
PORT = 8080

def request(content):
    conn = http.client.HTTPConnection(HOST, PORT)

    headers = { 'content-type': 'application/x-www-form-urlencoded', }
    body = 'full_data=' + urllib.parse.quote(content)
    conn.request('POST', '/api/v2', body=body, headers=headers)

    r = conn.getresponse()
    return r.read().decode()

def main():
    content = """34
0.39 0.62
0.395 0.58
0.4066666666666667 0.5133333333333333
0.43 0.4
0.43833333333333335 0.37333333333333335
0.4716666666666667 0.32
0.47833333333333333 0.30666666666666664
0.49666666666666665 0.3
0.5083333333333333 0.3
0.54 0.2866666666666667
0.5483333333333333 0.2833333333333333
0.5533333333333333 0.2833333333333333
0.565 0.2833333333333333
0.5716666666666667 0.2833333333333333
0.575 0.2866666666666667
0.59 0.31
0.5916666666666667 0.32
0.5933333333333334 0.33
0.6 0.36
0.605 0.41
0.61 0.4533333333333333
0.61 0.46
0.61 0.47
0.6016666666666667 0.56
0.6 0.5666666666666667
0.58 0.6133333333333333
0.5666666666666667 0.6466666666666666
0.5283333333333333 0.7266666666666667
0.485 0.8
0.4483333333333333 0.8533333333333334
0.44166666666666665 0.8533333333333334
0.435 0.8533333333333334
0.43333333333333335 0.8533333333333334
0.40166666666666667 0.8566666666666667"""
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
