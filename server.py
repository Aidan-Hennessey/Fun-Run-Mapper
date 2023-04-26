import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50008              # Arbitrary non-privileged port
curr_csock = None

def getline():
    global curr_csock
    if curr_csock == None:
        raise RuntimeError("bad")

    buffer = curr_csock.recv(1024)
    if not buffer: # connection ended
        return None
    while buffer[-1] != 10: # newline
        buffer += curr_csock.recv(1024)
    buffer = buffer[:-1] # cut off newline
    return buffer.decode('utf-8')

def main():
    global curr_csock
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ssock:
        ssock.bind((HOST, PORT))
        ssock.listen()
        csock, addr = ssock.accept()
        curr_csock = csock
        print('[+] recieved connection from', *addr)

        while True:
            buffer = getline()
            if not buffer:
                break
            print(f"[-] recieved {len(buffer.encode('utf8'))} bytes:", buffer)

            csock.sendall(b"got 'em\n")

if __name__ == "__main__":
    main()
