import os, sys,json,pickle
from colorama import Fore
import threading
import socket, json, time
from threading import Lock, Thread, Event



server_port = int(sys.argv[1])
num_proc = int(sys.argv[2])
num_simulations = int(sys.argv[3])

port_seed = 3000
MAX_CAPACITY = 8192

############################################

beatDict = {}

dictLock = Lock()


def update(remote_message):
        "Create or update a dictionary entry"
        dictLock.acquire()
        beatDict[remote_message["process_id"]] = remote_message
        dictLock.release()

def extractSilent(howPast):
    "Returns a list of entries older than howPast"
    silent = []
    when = time.time() - howPast
    #dictLock.acquire()
    for key in beatDict.keys(  ):
        if beatDict[key]["time_stamp"] < when:
            silent.append(beatDict[key])
    #dictLock.release()
    return silent

def extractAlive(howPast):
    "Returns a list of entries older than howPast"
    print(f"{Fore.RED} in extract alive {Fore.RESET}")
    silent = dict()
    when = time.time() - howPast
    dictLock.acquire()
    for key in beatDict.keys():
        if beatDict[key]["time_stamp"] >= when:
            # silent.append(beatDict[key])
            silent[key] = beatDict[key]


    dictLock.release()
    return silent



def heart_thread_function(hb_port):
    hb_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hb_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    

    print(f"heartbeat server before binding {hb_port}")
    hb_socket.bind(("localhost", hb_port))
    print("heartbeat socket binded to port", hb_port)

    while True:
        msg, addr = hb_socket.recvfrom(MAX_CAPACITY)
        msg = msg.decode()
        remoteMessage = json.loads(msg)

        update(remoteMessage)
        print(f"{beatDict=}")

        # silent_processes = extractSilent(5)
        # print(f"{silent_processes=}")

        print(f"{Fore.WHITE} Received  Heartbeat from {remoteMessage}")


HEART_BEAT_PORT = 1729


heart_thread = threading.Thread(target=heart_thread_function, args=(HEART_BEAT_PORT,))
heart_thread.start()

##############################


Live_checker_port = 2729

def sendAlive():
    hb_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hb_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    hb_socket.bind(("localhost", Live_checker_port))

    while True:

        msg, addr = hb_socket.recvfrom(MAX_CAPACITY)
        print(f"{Fore.YELLOW}received send alive socket{Fore.RESET}")
        #msg = msg.decode()
        #remoteMessage = json.loads(msg)

        #update(remoteMessage)
        #print(f"{beatDict=}")

        alive_processes = extractAlive(10)
        hb_socket.sendto(json.dumps(alive_processes).encode(), addr)


        # print(f"{alive_processes=}")
        # with open("alive.pkl","wb") as f:
        #     pickle.dump(alive_processes,f)
        
        time.sleep(2)
        #hb_socket.sendto(json.dumps(alive_processes).encode(), addr)



alive_thread = threading.Thread(target=sendAlive)
alive_thread.start()

###########################3
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
        # print(f"{request_type=}")
        request_json = json.loads(data)
        # print("recerved requsf for peerlist on server")

        node_data = {}
        with open("config.txt", "r") as fp:
            content = fp.readlines()
            # print(f"{content=}")

            for line in content:
                if len(line) < 2: continue

                line = line.split(",")
                node_data[line[0]] = ("localhost",int(line[1].strip()))

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
