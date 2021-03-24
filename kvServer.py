import logging
import socket
import collections
import getopt
import json
import sys
import threading
import time
import pickle
from trie import TrieNode


available_options = "a:p:"
options = collections.defaultdict()
try:
    args, values = getopt.getopt(sys.argv[1:], available_options)

    for k, v in args:
        options[k[1:]] = v

except getopt.error as err:
    print(str(err))
    sys.exit(2)

print(options.items())

ADDR = (options['a'], int(options['p']))

# Create a Socket ( connect two computers)
def create_socket():
    try:
        global s
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global s
        print("Binding the Port: " + str(ADDR))

        s.bind(ADDR)
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


# Handling connection from multiple clients and saving to a list
# Closing previous connections when server.py file is restarted
def accepting_connections():
    global s
    global conn
    global address
    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout

            print("Connection has been established :" + address[0])
            accept_payload()

        except:
            print("Error accepting connections")



def accept_payload():
    global conn
    global address

    store = TrieNode('*')

    connected = True
    while connected:
        payload = conn.recv(1024).decode('utf-8')
        if payload:
            if '!DISCONNECT' in payload:
                connected = False
                conn.close()
            elif 'OPTIONS' in payload:
                print('OPTIONS received')
                response = {
                    'code': 200,
                    'status': 'Success'
                }
                response = json.dumps(response)
                conn.send(response.encode('utf-8'))
            elif 'PUT' in payload:
                print('PUT received')
                print(f"[{address}] {payload}")
                req_method, data = payload.split(' ')
                print(req_method)
                print(data)
                key, value = data.split(':', 1)
                value = json.loads(value)
                print(key)
                print(value)
                conn.send("OK - 200 ".encode('utf-8'))
            elif 'GET' in payload:
                pass
            elif 'DELETE' in payload:
                pass
            elif 'QUERY' in payload:
                pass
            else:
                print('FUCK YOU')
                conn.send("NOT FOUND - 404 ".encode('utf-8'))




# Create worker threads
def setup_server():
    init_socket()
    accept_payload()

    # t = threading.Thread(target=init_socket)
    # t.daemon = True
    # t2 = threading.Thread(target=accept_payload)
    # t2.daemon = True
    # a = [t, t2]
    # for ta in a:
    #     ta.start()



# Do next job that is in the queue (handle connections, send commands)
def init_socket():
    create_socket()
    bind_socket()
    accepting_connections()


setup_server()

