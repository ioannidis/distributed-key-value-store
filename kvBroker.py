import errno
import pickle
import random
import socket
import collections
import sys
import getopt
import threading
import time
import tokenize

from utils.parser import Parser
from utils.request import Request
from utils.response import Response


class KvBroker:

    def __init__(self, options) -> None:
        self._options = options
        self._configuration, self._sockets = self.init_connections()
        self.init_data()
        self.start_shell()

    def init_connections(self):
        f = open(self._options['s'], 'r')
        configuration = f.readlines()
        f.close()

        sockets = {}
        for c in configuration:
            try:
                ip, port = c.split(' ')
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((ip, int(port)))
                sockets[(ip, int(port))] = new_socket
            except socket.error as e:
                print(str(e) + " " + ip + ":" + str(port))

        # Check if there are enough
        # if len(sockets) < int(self._options['k']):
        #     print('[ERROR] Number of servers is lower than the replication number')
        #     exit()

        return configuration, sockets

    def load_data(self):
        return Parser.file_serializer(self._options['i'])

    def init_data(self):
        data = self.load_data()
        for d in data:
            req = Request('PUT', d)
            rdm_sockets = random.sample(list(self._sockets.keys()), int(self._options['k']))

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
            if results[200]:
                print(f'{query} : {results[200]}')
            else:
                print(f'{query} : ''{''}')
        elif 404 in results:
            print(f'{query} : NOT FOUND')
        elif 400 in results:
            print(f'BAD REQUEST')
        elif 422 in results:
            print(f'[Error | Invalid data format] {results[422]}')

    # Start the terminal interface for accepting new requests
    def start_shell(self):
        while True:
            cmd = input('kvStore> ').strip()

            if not cmd:
                continue

            if cmd == '!DISCONNECT':
               pass

            else:
                self._heart_beat()
                is_replication_valid = self._is_replication_valid()
                req_type, payload = cmd.split(' ', 1)

                if req_type == 'PUT':
                    req = Request(req_type, payload)
                    rdm_sockets = random.sample(list(self._sockets.keys()), int(self._options['k']))

                    result = {}
                    for ip in rdm_sockets:
                        self._stream(req, ip, result)
                        # try:
                        #     cur_socket = self._sockets[i]
                        #
                        #     # Send request OPTIONS
                        #     cur_socket.send(req.get_options())
                        #     pickle.loads(cur_socket.recv(100))
                        #
                        #     # Send request
                        #     cur_socket.send(req.get_request())
                        #
                        #     # Receive response's OPTIONS
                        #     res_options = pickle.loads(cur_socket.recv(100))
                        #     # Send confirmation
                        #     confirm = Response()
                        #     cur_socket.send(confirm.get_response())
                        #
                        #     # Receive response
                        #     res = pickle.loads(cur_socket.recv(res_options['res_size']))
                        #
                        #     result[res['code']] = res['payload']
                        #
                        # except socket.error as e:
                        #     print(f'[Error] {e}')
                        # except EOFError as e:
                        #     pass
                        #     del self._sockets[i]

                    self.print_result(payload, result)

                elif req_type == 'GET' or req_type == 'QUERY':
                    result = {}
                    req = Request(req_type, payload)

                    for ip in self._sockets.keys():
                        self._stream(req, ip, result)
                        # try:
                        #     # Send request's OPTIONS
                        #     cur_socket.send(req.get_options())
                        #     pickle.loads(cur_socket.recv(100))
                        #
                        #     # Send requests
                        #     cur_socket.send(req.get_request())
                        #
                        #     # Receive response's OPTIONS
                        #     res_options = pickle.loads(cur_socket.recv(100))
                        #     # Send confirmation
                        #     confirm = Response()
                        #     cur_socket.send(confirm.get_response())
                        #
                        #     # Receive response
                        #     res = pickle.loads(cur_socket.recv(res_options['res_size']))
                        #
                        #     result[res['code']] = res['payload']
                        #
                        # except socket.error as e:
                        #     print(f'[Error] {e}')
                        # except EOFError as e:
                        #     pass
                        #     # del self._sockets[ip]

                    if not is_replication_valid:
                        print(f'[WARNING] Data may be inconsistent. More than {int(self._options["k"])} servers are unavailable!')

                    self.print_result(payload, result)

                elif req_type == 'DELETE':
                    if not self._is_all_servers_available():
                        print('[WARNING] Cannot perform delete operation. One or more servers are unavailable!')
                        continue

                    result = {}
                    ip_address = list(self._sockets.keys())
                    req = Request(req_type, payload)
                    for ip in ip_address:
                        self._stream(req, ip, result)
                        # try:
                        #
                        #     cur_socket = self._sockets[ip]
                        #
                        #     # Send request's OPTIONS
                        #     cur_socket.send(req.get_options())
                        #     pickle.loads(cur_socket.recv(100))
                        #
                        #     # Send request
                        #     cur_socket.send(req.get_request())
                        #
                        #     # Receive response's OPTIONS
                        #     res_options = pickle.loads(cur_socket.recv(100))
                        #     # Send confirmation
                        #     confirm = Response()
                        #     cur_socket.send(confirm.get_response())
                        #
                        #     # Receive response
                        #     res = pickle.loads(cur_socket.recv(res_options['res_size']))
                        #
                        #     result[res['code']] = res['payload']
                        #
                        # except socket.error as e:
                        #     print(f'[Error] {e}')
                        # except EOFError as e:
                        #     pass
                        #     # del self._sockets[ip]
                else:
                    pass
                    # TODO: na ftiakso auto edo

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
        if len(self._sockets) < int(self._options['k']):
            sys.exit('[Error] Not enough servers to support replication! Please restart the servers!')

        return len(self._configuration) - len(self._sockets) < int(self._options['k'])

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
        except EOFError as e:
            pass
        #     del self._sockets[i]



if __name__ == '__main__':

    available_options = "s:i:k:"
    options = collections.defaultdict()
    try:
        args, values = getopt.getopt(sys.argv[1:], available_options)

        for k, v in args:
            options[k[1:]] = v

    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    print(options.items())

    kv_broker = KvBroker(options)