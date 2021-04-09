import argparse
import pickle
import random
import socket
import sys

from utils.parser import Parser
from utils.request import Request
from utils.response import Response


class KvBroker:

    def __init__(self, options) -> None:
        self._options = options
        self._configuration, self._sockets = self.init_connections()
        print('=== Welcome to kvBroker ===')
        self.init_data()
        self.start_shell()

    def init_connections(self):
        try:
            f = open(self._options.s, 'r')
            configuration = f.readlines()
            f.close()
        except FileNotFoundError as e:
            sys.exit(f'{e}')

        sockets = {}
        for c in configuration:
            try:
                ip, port = c.split(' ')
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((ip, int(port)))
                sockets[(ip, int(port))] = new_socket
            except socket.error as e:
                print(str(e) + " " + ip + ":" + str(port))

        # Check if there are enough servers available to support replication
        if len(sockets) < int(self._options.k):
            print('[ERROR] Number of servers is lower than the replication number')
            exit()

        return configuration, sockets

    # Load and parse data from the given file
    def load_data(self):
        return Parser.file_serializer(self._options.i)

    # Initialize data with respect to replication factor
    def init_data(self):
        print('Data initialization...')
        data = self.load_data()
        for d in data:
            req = Request('PUT', d)
            rdm_sockets = random.sample(list(self._sockets.keys()), self._options.k)

            for i in rdm_sockets:
                cur_socket = self._sockets[i]

                # Send request's OPTIONS
                cur_socket.send(req.get_options())
                cur_socket.recv(100)

                # Send request
                cur_socket.send(req.get_request())

                # Receive response's OPTIONS
                res_options = pickle.loads(cur_socket.recv(100))
                # Send confirmation
                confirm = Response()
                cur_socket.send(confirm.get_response())

                # Receive response
                res = pickle.loads(cur_socket.recv(res_options['res_size']))


    def print_result(self, query, results):
        if 200 in results:
            print(f'{query} : {results[200]}')
        elif 201 in results:
            print(f'{results[201]}')
        elif 404 in results:
            print(f'{query} : {results[404]}')
        elif 400 in results:
            print(f'{results[400]}')
        elif 422 in results:
            print(f'[Error | Invalid data format] {results[422]}')

    # Start the terminal interface for accepting new requests
    def start_shell(self):
        while True:
            cmd = input('kvStore> ').strip()

            if not cmd:
                continue

            if cmd == '!DISCONNECT':
                sys.exit('kvBroker has been disconnected! Bye!')

            else:
                self._heart_beat()
                is_replication_valid = self._is_replication_valid()
                req_type, payload = cmd.split(' ', 1)

                if req_type == 'PUT':
                    req = Request(req_type, payload)
                    rdm_sockets = random.sample(list(self._sockets.keys()), self._options.k)

                    result = {}
                    for ip in rdm_sockets:
                        self._stream(req, ip, result)

                    self.print_result(payload, result)

                elif req_type == 'GET' or req_type == 'QUERY':
                    result = {}
                    req = Request(req_type, payload)

                    for ip in self._sockets.keys():
                        self._stream(req, ip, result)

                    if not is_replication_valid:
                        print(f'[WARNING] Data may be inconsistent. More than {self._options.k} servers are unavailable!')

                    self.print_result(payload, result)

                elif req_type == 'DELETE':
                    if not self._is_all_servers_available():
                        print('[WARNING] Cannot perform delete operation. One or more servers are unavailable!')
                        continue

                    result = {}
                    req = Request(req_type, payload)
                    for ip in self._sockets.keys():
                        self._stream(req, ip, result)

                    self.print_result(payload, result)

                else:
                    print('[INFO] Invalid request type!')
                    print('[INFO] Supported types: PUT | GET | QUERY | DELETE')

    # Send hear beat request to check the status of the servers
    def _heart_beat(self):
        req = Request('HEART_BEAT')

        ip_address = list(self._sockets.keys())
        for ip in ip_address:
            try:
                # Send request's OPTIONS
                self._sockets[ip].send(req.get_options())
                pickle.loads(self._sockets[ip].recv(100))

                # Send request
                self._sockets[ip].send(req.get_request())
                # Receive response
                pickle.loads(self._sockets[ip].recv(100))

            except socket.error as e:
                print(f'[Error] {e}')
            except EOFError as e:
                del self._sockets[ip]

    # Check server availability
    def _is_all_servers_available(self):
        return len(self._sockets) == len(self._configuration)

    # Check if replication rules are valid
    def _is_replication_valid(self):
        if len(self._sockets) < self._options.k:
            sys.exit('[Error] Not enough servers to support replication! Please restart the servers!')

        return len(self._configuration) - len(self._sockets) < self._options.k

    # Send data to the servers
    def _stream(self, req, ip,  result):
        try:
            cur_socket = self._sockets[ip]

            # Send request OPTIONS
            cur_socket.send(req.get_options())
            pickle.loads(cur_socket.recv(100))

            # Send request
            cur_socket.send(req.get_request())

            # Receive response's OPTIONS
            res_options = pickle.loads(cur_socket.recv(100))
            # Send confirmation
            confirm = Response()
            cur_socket.send(confirm.get_response())

            # Receive response
            res = pickle.loads(cur_socket.recv(res_options['res_size']))

            result[res['code']] = res['payload']

        except socket.error as e:
            print(f'[Error] {e}')


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='kvBroker')
    args_parser.add_argument('-s', '--serverFile', dest='s', type=str, default='serverFile.txt', metavar='', required=True, help='The serverFile is a space separated list of server IPs and their respective ports that will be listening for queries and indexing commands.')
    args_parser.add_argument('-i', '--dataToIndex', dest='i', type=str, default='dataToIndex.txt', metavar='', required=True, help='The dataToIndex is a file containing data that was generated using the data generator.')
    args_parser.add_argument('-k', '--kReplication', dest='k', type=int, default=1, metavar='', required=True, help='The k value is the replication factor.')
    args = args_parser.parse_args()

    if args.k < 1:
        sys.exit('[Error] Replication factor should be greater equal to 1.')

    kv_broker = KvBroker(args)
