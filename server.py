import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50008              # Arbitrary non-privileged port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ssock:
    ssock.bind((HOST, PORT))
    ssock.listen()
    csock, addr = ssock.accept()
    print('[+] recieved connection from', *addr)

    while True:
        buffer = csock.recv(1024)
        if not buffer: # connection ended
            break
        while buffer[-1] != 10: # newline
            buffer += csock.recv(1024)
        print(f'[-] recieved {len(buffer)} bytes:', buffer)

        string = buffer.decode('utf-8')
        csock.sendall(b"got 'em\n")
