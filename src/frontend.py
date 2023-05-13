from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

from os import chdir
chdir("../../website/dist/")

PORT = 8000

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='/etc/letsencrypt/live/sky.jason.cash/fullchain.pem', keyfile='/etc/letsencrypt/live/sky.jason.cash/privkey.pem')

httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

httpd.serve_forever()
