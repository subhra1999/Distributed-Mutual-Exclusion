
# import socket programming library
import socket, json, time
import sys, logging
import ra_mutex as ricart_agrawala

from colorama import Fore

# import thread module
from _thread import *
import threading

self_id = int(sys.argv[1])
self_port = int(sys.argv[2])
server_port = int(sys.argv[3])
num_simuations = int(sys.argv[4])
#print(f"{server_port=}")

print_lock = threading.Lock()

# thread function
#############################3
# thread for sending heartbeat

SERVER_HEART_BEAT_PORT = 1729

def heart_beat_sender_thread():
    #print("Started heartbeat thread, 5 secs interaval")
    client_socket_hb = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket_hb.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    msg = {
        "process_id": self_id,
        "port":self_port,
        "msg_type":"ZINDA",
        "time_stamp": time.time()
    }

    while True:
        msg["time_stamp"] = time.time()
        client_socket_hb.sendto(json.dumps(msg).encode(), ("localhost", int(SERVER_HEART_BEAT_PORT)))
        time.sleep(2)
    # data = server_socket.recv(1024)


client_heart_thread = threading.Thread(target=heart_beat_sender_thread)
client_heart_thread.start()


#############################################
def thread_for_accepting_connections():
    while True:
        logging.debug("Received connection")
        # data received from client
        receivingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = receivingSocket.recv(4096)
        # data = c.recv(1024)
        #print(f"Request data={data.decode()}")
        with open("./log.txt", "a") as f:
            f.write(f"received request at {self_id} , {self_port}")
        #
        if not data:
            #print('Boye')

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
    #print(f"received in process {data_json=}")
    for key,val in data_json.items():
        message = f"REQUEST {key} time"
        sendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sendingSocket.sendto(str(message).encode(), ("localhost", int(val)))
        #print(message)
    # print(f"Received {data!r}")

    # ask main server for lisst of peers

    # establish connection with peers

    # send reqeusts to peers

    pass


def start_process_communication():
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("localhost", self_port))
    print("socket binded to port", self_port)

    # put the socket into listening mode
    # s.listen(5)
    # print("socket is listening")

    with open("config.txt", "a") as fp:
        lines = [f"\n{self_id}, {self_port}"]
        fp.writelines(lines)
    

    # talk to main server in  a separate thread.
    # start_new_thread(thread_for_request, (server_port,))

    # a forever loop until client wants to exit

    i_sim_count = 1
    while True:

    # for i in range(num_simuations):
        
            

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        msg = {
            "process_id": self_id,
            "port":self_port
        }
        server_socket.sendto(json.dumps(msg).encode(), ("localhost", int(server_port)))
        data = server_socket.recv(1024)

        data_json = json.loads(data.decode())


        localAddr = ("localhost", int(self_port))
        procPID = self_id
        procName = self_id
        remoteAddr = data_json
        numRemotes = len(data_json)


        if i_sim_count <= num_simuations:
            if i_sim_count == 1:
                time.sleep(5)
            ricart_agrawala.initialize_mutex(localAddr, procPID, procName, remoteAddr, numRemotes, s)
            # time.sleep(2)
            while(not ricart_agrawala.lock_mutex()): pass

            sleep_interval = 10 * (self_id + 1)
            time.sleep(sleep_interval)
            ricart_agrawala.release_mutex()
            #time.sleep(5)

            #print("sleeping for next request 10 second")
            time.sleep(10)
            #print("goint for next request after 10 seconds")

            i_sim_count += 1
            # break
            
            #print(f"{Fore.CYAN} NEXT ITERATION {i_sim_count} {Fore.RESET}\n\n")

            #print("-------------------------------------------------------------------------------------------------------------")

            #print("\n\n\n\n")


    s.close()


if __name__ == '__main__':
    #time.sleep(5)
    start_process_communication()
