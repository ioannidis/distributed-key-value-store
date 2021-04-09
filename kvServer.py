import argparse
import socket
import json
import pickle
from json import JSONDecodeError

from trie import TrieNode
from utils.parser import Parser
from utils.response import Response



class KvServer:

    def __init__(self, options) -> None:
        self._address = (options.a, options.p)
        self._broker_address = None
        self._socket = self._create_socket()
        self._conn = None
        self._store = None
        self._bind_socket()
        self._accepting_connections()

    # Create a Socket ( connect two computers)
    def _create_socket(self):
        try:
            return socket.socket()
        except socket.error as msg:
            print("[Error] Socket creation error: " + str(msg))

    # Binding the socket and listening for connections
    def _bind_socket(self):
        try:
            print("Binding the Port: " + str(self._address))
            self._socket.bind(self._address)
            self._socket.listen(5)
        except socket.error as msg:
            print("[Error] Socket binding error" + str(msg) + "\n" + "Retrying...")
            self._bind_socket()

    # Accept new connections
    # Closing previous connections when kvBroker file is restarted
    def _accepting_connections(self):
        while True:
            try:
                self._conn, self._broker_address = self._socket.accept()
                self._socket.setblocking(True)
                print("[Info] Connection has been established :" + self._broker_address[0])
                self._request_handler()

            except Exception as e:
                print("[Info] KvBroker has been disconnected!")

    # Handle the incoming requests
    def _request_handler(self):
        self._store = TrieNode('*', is_root=True)

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
                    self._put_mapping(req)

                elif req['req_type'] == 'GET':
                    self._get_mapping(req)

                elif req['req_type'] == 'DELETE':
                    self._delete_mapping(req)

                elif req['req_type'] == 'QUERY':
                    self._query_mapping(req)

                elif req['req_type'] == 'HEART_BEAT':
                    self._heart_beat_mapping()

                else:
                    res = Response(400, 'BAD REQUEST', 'BAD REQUEST')
                    self._send_response(res)

    # GET handler
    def _get_mapping(self, req):
        print(f"[{self._broker_address} | GET] {req['payload']}")

        node = self._store.find(req['payload'])
        if isinstance(node, TrieNode):
            result = {}
            node.res_builder('', result, 0)
            res = Response(200, 'OK', json.dumps(result).replace(',', ';'))
        elif isinstance(node, str) or isinstance(node, dict):
            res = Response(200, 'OK', json.dumps(node))
        else:
            res = Response(404, 'NOT FOUND', 'NOT FOUND')

        # Send response
        self._send_response(res)

    # QUERY handler
    def _query_mapping(self, req):
        print(f"[{self._broker_address} | QUERY] {req['payload']}")

        node = self._store.find_path(req['payload'])
        if isinstance(node, TrieNode):
            result = {}
            node.res_builder('', result, 0)
            res = Response(200, 'OK', json.dumps(result).replace(',', ';'))
        elif isinstance(node, str) or isinstance(node, int) or isinstance(node, float) or isinstance(node, dict):
            res = Response(200, 'OK', json.dumps(node))
        else:
            res = Response(404, 'NOT FOUND', 'NOT FOUND')

        # Send response
        self._send_response(res)

    # PUT handler
    def _put_mapping(self, req):
        print(f"[{self._broker_address} | PUT] {req['payload']}")

        key, value = req['payload'].split(':', 1)

        try:
            decoded_value = json.loads(Parser.serialize(value))

            if isinstance(decoded_value, str):
                raise JSONDecodeError(msg='Input does not follow the key:value format', doc=value, pos=0)

            # If key already exists, remove it in order to store the incoming data
            node = self._store.find(key.strip('"'))
            if isinstance(node, TrieNode) or isinstance(node, str) or isinstance(node, int) or isinstance(node, float) or isinstance(node, dict):
                self._store.remove(key.strip('"'))

            # Store data
            self._store.insert(key.strip('"'), decoded_value)
            # Prepare response
            res = Response(201, 'OK', 'CREATED')
        except JSONDecodeError as e:
            # Prepare response
            res = Response(422, 'ERROR - INVALID DATA', f'Failed at pos {e.pos} - {e.msg}')

        # Send response
        self._send_response(res)

    # DELETE handler
    def _delete_mapping(self, req):
        print(f"[{self._broker_address} | DELETE] {req['payload']}")

        if self._store.remove(req['payload']):
            res = Response(200, 'OK', 'DELETED')
        else:
            res = Response(404, 'NOT FOUND', 'IS NOT ROOT KEY')

        # Send response
        self._send_response(res)

    # Heart beat handler
    def _heart_beat_mapping(self):
        res = Response()
        self._conn.send(res.get_response())

    # Send OPTIONS and response
    def _send_response(self, res):
        self._conn.send(res.get_options())
        self._conn.recv(100)
        self._conn.send(res.get_response())


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='kvServer')
    args_parser.add_argument('-a', '--ipAddress', dest='a', type=str, metavar='', required=True,
                             help='Server\'s ip address.')
    args_parser.add_argument('-p', '--port', dest='p', type=int, metavar='', required=True,
                             help='Server\'s port.')
    args = args_parser.parse_args()

    kv_server = KvServer(args)
