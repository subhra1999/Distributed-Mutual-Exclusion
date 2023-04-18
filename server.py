import os, sys,json


server_port = int(sys.argv[1])
num_proc = int(sys.argv[2])
num_simulations = int(sys.argv[3])

port_seed = 3000

# listen on port 3000

# import socket programming library
import socket

# import thread module
from _thread import *
import threading

print_lock = threading.Lock()



def Main():
    host = ""

    # reserve a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = server_port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    

    print(f"server before binding {port}")
    s.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    # s.listen(50)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:

        # data received from client
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data, addr = s.recvfrom(4096)
        # data = .recv(1024)
        if not data:
            print('Boye')
            
            # lock released on exit
            print_lock.release()
            break

        # reverse the given string from client
        # data = data[::-1]
        request_type = data
        print(f"{request_type=}")
        request_json = json.loads(data)
        print("recerved requsf for peerlist on server")

        node_data = {}
        with open("config.txt", "r") as fp:
            content = fp.readlines()
            print(f"{content=}")

            for line in content:
                if len(line) < 2: continue

                line = line.split(",")
                node_data[line[0]] = line[1]

            # convert to json and send reply

            # send back reversed string to client
            # c.send(json.dumps(node_data).encode())
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.sendto(json.dumps(node_data).encode(), addr)

    # connection closed
    # c.close()
    # print_lock.release()

    s.close()


if __name__ == '__main__':
    Main()
