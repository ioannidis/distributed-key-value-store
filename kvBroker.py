import itertools
import socket
import select
import collections
import sys
import getopt


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

f = open(options['s'], 'r')
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

# if len(sockets) < int(options['k']):
#     print('[ERROR] Number of servers is lower than the replication number')
#     while sockets:
#         socket = sockets.popleft()
#         socket.close()
#     exit()


f = open(options['i'], 'r')
data = f.readlines()
f.close()


def init_data():
    for d in data:
        for _ in range(int(options['k'])):
            cur_socket = sockets.popleft()
            cur_socket.sendall(('PUT ' + d).encode('utf-8'))
            cur_socket.recv(1024)  # Do stuff
            sockets.append(cur_socket)


def start_shell():
    while True:
        cmd = input('kvStore> ')
        for _ in range(int(options['k'])):
            cur_socket = sockets.popleft()
            cur_socket.send(cmd.encode('utf-8'))
            print(cur_socket.recv(1024)) # Do stuff
            sockets.append(cur_socket)




# init_data()
start_shell()

# user_input = input('Write your message: ')
#
# for _ in range(int(options['k'])):
#     cur_socket = sockets.popleft()
#     cur_socket.sendall(user_input.encode('utf-8'))
#     cur_socket.recv(1024)  # Do stuff
#     sockets.append(cur_socket)


# sockets = {}
# for c in configuration:
#     ip, port = c.split(' ')
#     new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     new_socket.connect((ip, int(port)))
#     sockets[new_socket.fileno()] = new_socket
#
# poll = select.poll()
# for k in sockets.keys():
#     poll.register(k)
#
# while True:
#     user_input = input('Write your message: ')
#     fd = poll.poll()  # Optional timeout parameter in seconds
#     socket = sockets[fd[0][0]]
#     socket.sendall(user_input.encode('utf-8'))
#     socket.recv(1024)  # Do stuff


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b'Hello, world')
#     data = s.recv(1024)

# print('Received', repr(data))