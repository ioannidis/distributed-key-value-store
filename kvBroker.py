import errno
import pickle
import socket
import collections
import sys
import getopt
import tokenize

from utils.request import Request


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

        sockets = collections.deque([])
        for c in configuration:
            try:
                ip, port = c.split(' ')
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((ip, int(port)))
                sockets.append(new_socket)
            except socket.error as err:
                print(str(err) + " " + ip + ":" + str(port))

        # Check if there are enough
        # if len(sockets) < int(self._options['k']):
        #     print('[ERROR] Number of servers is lower than the replication number')
        #     exit()

        return configuration, sockets

    def load_data(self):
        f = open(self._options['i'], 'r')
        data, line = [], []
        for token in tokenize.generate_tokens(f.readline):
            if token[0] == tokenize.NEWLINE:
                data.append("".join(line))
                line = []
            elif token[0] == tokenize.OP and token[1] == ';':
                line.append(',')
            else:
                line.append(token[1])
        f.close()
        return data

    def init_data(self):
        data = self.load_data()
        for d in data:
            req = Request('PUT', d)
            for _ in range(int(options['k'])):

                cur_socket = self._sockets.popleft()

                cur_socket.send(req.get_options())
                cur_socket.recv(100)

                cur_socket.send(req.get_request())
                cur_socket.recv(1024)

                self._sockets.append(cur_socket)

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

    def start_shell(self):
        while True:
            cmd = input('kvStore> ').strip()
            req_type, payload = cmd.split(' ', 1)

            if '!DISCONNECT' in cmd:
                cur_socket = self._sockets.popleft()
                cur_socket.send(cmd.encode('utf-8'))

            else:
                if req_type == 'PUT':
                    req = Request(req_type, payload)
                    for _ in range(int(self._options['k'])):
                        try:
                            cur_socket = self._sockets.popleft()

                            cur_socket.send(req.get_options())
                            pickle.loads(cur_socket.recv(100))

                            cur_socket.send(req.get_request())
                            pickle.loads(cur_socket.recv(5000))

                            self._sockets.append(cur_socket)
                        except socket.error as e:
                            print('Socket error')
                        except IOError as e:
                            if e.errno == errno.EPIPE:
                                print('Server is unreachable')

                elif req_type == 'GET' or req_type == 'QUERY':
                    result = {}
                    for _ in range(len(self._sockets)):
                        try:
                            req = Request(req_type, payload)

                            cur_socket = self._sockets.popleft()

                            cur_socket.send(req.get_options())
                            pickle.loads(cur_socket.recv(100))

                            cur_socket.send(req.get_request())
                            res = pickle.loads(cur_socket.recv(5000))

                            self._sockets.append(cur_socket)

                            result[res['code']] = res['payload']

                        except socket.error as e:
                            print('Socket error')
                        except IOError as e:
                            if e.errno == errno.EPIPE:
                                print('Server is unreachable')

                    self.print_result(payload, result)

                elif req_type == 'DELETE':
                    if len(self._configuration) != len(self._sockets):
                        print('[WARNING] Cannot perform delete operation - One or more servers may be unavailable')
                    else:
                        result = {}
                        for _ in range(len(self._sockets)):
                            try:
                                req = Request(req_type, payload)

                                cur_socket = self._sockets.popleft()

                                cur_socket.send(req.get_options())
                                res = cur_socket.recv(100)
                                if not res:
                                    print('[WARNING] Cannot perform delete operation - One or more servers may be unavailable')
                                    continue
                                pickle.loads(res)

                                cur_socket.send(req.get_request())
                                res = pickle.loads(cur_socket.recv(5000))

                                self._sockets.append(cur_socket)

                                result[res['code']] = res['payload']

                            except socket.error as e:
                                print('Socket error')
                            except IOError as e:
                                if e.errno == errno.EPIPE:
                                    print('Server is unreachable')
                else:
                    pass
                    # TODO: na ftiakso auto edo


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
