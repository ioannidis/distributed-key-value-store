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
from utils.response import Response

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
        # Receive OPTION request
        req = conn.recv(100)
        options = pickle.loads(req)
        res = Response()
        conn.send(res.get_response())
        # Receive request
        req = conn.recv(options['req_size'])
        req = pickle.loads(req)

        if req:
            if req['req_type'] == 'PUT':
                print(f"[{address} | PUT] {req['payload']}")

                key, value = req['payload'].split(':', 1)
                store.insert(key[1:-1], json.loads(value))

                res = Response()
                conn.send(res.get_response())
            elif req['req_type'] == 'GET':
                print(f"[{address} | GET] {req['payload']}")

                node = store.find(req['payload'])
                if node:
                    if not isinstance(node, TrieNode):
                        result = node
                    else:
                        result = {}
                        node.res_builder(node, '', result, 0)

                    res = Response(200, 'OK', result)
                else:
                    res = Response(404, 'NOT FOUND')
                conn.send(res.get_response())

            elif req['req_type'] == 'DELETE':
                print(f"[{address} | DELETE] {req['payload']}")

                if store.remove(req['payload']):
                    res = Response(200, 'OK')
                else:
                    res = Response(404, 'NOT FOUND')
                conn.send(res.get_response())

            elif req['req_type'] == 'QUERY':
                print(f"[{address} | QUERY] {req['payload']}")

                node = store.find_path(req['payload'])
                if node:
                    if not isinstance(node, TrieNode):
                        result = node
                    else:
                        result = {}
                        node.res_builder(node, '', result, 0)

                    res = Response(200, 'OK', result)
                else:
                    res = Response(404, 'NOT FOUND')
                conn.send(res.get_response())

            elif req['req_type'] == 'COMMAND':
                connected = False
                conn.close()
                exit()

            else:
                res = Response(400, 'BAD REQUEST')
                conn.send(res.get_response())




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

