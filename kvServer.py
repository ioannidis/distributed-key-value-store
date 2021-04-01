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



class KvServer:

    def __init__(self, options) -> None:
        self._options = options
        self._address = (options['a'], int(options['p']))
        self._broker_address = None
        self._socket = self._create_socket()
        self._conn = None
        self._bind_socket()
        self._accepting_connections()

    # Create a Socket ( connect two computers)
    def _create_socket(self):
        try:
            return socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    # Binding the socket and listening for connections
    def _bind_socket(self):
        try:
            print("Binding the Port: " + str(self._address))
            self._socket.bind(self._address)
            self._socket.listen(5)
        except socket.error as msg:
            print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
            self._bind_socket()

    # Handling connection from multiple clients and saving to a list
    # Closing previous connections when server.py file is restarted
    def _accepting_connections(self):
        while True:
            try:
                self._conn, self._broker_address = self._socket.accept()
                self._socket.setblocking(1)  # prevents timeout
                print("Connection has been established :" + self._broker_address[0])
                self._accept_payload()

            except:
                print("[Info] KvBroker has been disconnected!")

    def _accept_payload(self):
        store = TrieNode('*', is_root=True)

        connected = True
        while connected:
            # Receive OPTION request
            req = self._conn.recv(100)
            options = pickle.loads(req)
            res = Response()
            self._conn.send(res.get_response())
            # Receive request
            req = self._conn.recv(options['req_size'])
            req = pickle.loads(req)

            if req:
                if req['req_type'] == 'PUT':
                    print(f"[{self._broker_address} | PUT] {req['payload']}")

                    key, value = req['payload'].split(':', 1)
                    store.insert(key[1:-1], json.loads(value))

                    res = Response()
                    self._conn.send(res.get_response())

                elif req['req_type'] == 'GET':
                    print(f"[{self._broker_address} | GET] {req['payload']}")

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
                    self._conn.send(res.get_response())

                elif req['req_type'] == 'DELETE':
                    print(f"[{self._broker_address} | DELETE] {req['payload']}")

                    if store.remove(req['payload']):
                        res = Response(200, 'OK')
                    else:
                        res = Response(404, 'NOT FOUND')
                    self._conn.send(res.get_response())

                elif req['req_type'] == 'QUERY':
                    print(f"[{self._broker_address} | QUERY] {req['payload']}")

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
                    self._conn.send(res.get_response())

                elif req['req_type'] == 'COMMAND':
                    connected = False
                    self._conn.close()
                    exit()

                else:
                    res = Response(400, 'BAD REQUEST')
                    self._conn.send(res.get_response())


if __name__ == '__main__':
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

    kv_server = KvServer(options)

