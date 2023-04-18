
# import socket programming library
import socket, json
import sys, logging
import RicartAgrawala as ricart_agrawala

# import thread module
from _thread import *
import threading

self_id = int(sys.argv[1])
self_port = int(sys.argv[2])
server_port = int(sys.argv[3])
print(f"{server_port=}")

print_lock = threading.Lock()

# thread function


def thread_for_accepting_connections():
    while True:
        logging.debug("Received connection")
        # data received from client
        receivingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = receivingSocket.recv(4096)
        # data = c.recv(1024)
        print(f"Request data={data.decode()}")
        with open("./log.txt", "a") as f:
            f.write(f"received request at {self_id} , {self_port}")
        #
        if not data:
            print('Boye')

            # lock released on exit
            print_lock.release()
            break

        # reverse the given string from client
        data = data[::-1]

        # send back reversed string to client
        #c.send(data)

    # connection closed
    # c.close()


def thread_for_request(server_port):
    # establish connection with main server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # server_socket.connect(("localhost", server_port))

    msg = {
        "process_id": self_id,
        "port":self_port
    }
    server_socket.sendto(json.dumps(msg).encode(), ("localhost", int(server_port)))
    data = server_socket.recv(1024)

    data_json = json.loads(data.decode())
    print(f"received in process {data_json=}")
    for key,val in data_json.items():
        message = f"REQUEST {key} time"
        sendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sendingSocket.sendto(str(message).encode(), ("localhost", int(val)))
        print(message)
    # print(f"Received {data!r}")

    # ask main server for lisst of peers

    # establish connection with peers

    # send reqeusts to peers

    pass


def Main():
    host = ""

    # reserve a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = self_port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    # s.listen(5)
    print("socket is listening")

    with open("config.txt", "a") as fp:
        lines = [f"\n{self_id}, {self_port}"]
        fp.writelines(lines)

    # talk to main server in  a separate thread.
    start_new_thread(thread_for_request, (server_port,))

    # a forever loop until client wants to exit
    while True:

        # establish connection with client
        # c, addr = s.accept()
        message, address = s.recvfrom(4096)

        print(f"received {message} from {address} in process {self_id}")



        # Start a new thread and return its identifier
        start_new_thread(thread_for_accepting_connections, ())

    s.close()


if __name__ == '__main__':
    Main()
