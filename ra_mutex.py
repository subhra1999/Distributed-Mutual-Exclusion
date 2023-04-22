import sys, time, threading, socket, json, colorama,pickle
from colorama import *


Live_checker_port = 2729


def send_message(addr, message):
    #print(f"{current_process_info['procPID']} sending message")
    sendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendingSocket.sendto(str(message).encode(), addr)
    sendingSocket.close()

    #print(f'{current_process_info["procPID"]}  message sent')


def thread_message_listener(listening_socket):
    

    while True:
        msg, addr = listening_socket.recvfrom(MAX_CAPACITY)
        msg = msg.decode()
        remoteMessage = json.loads(msg)
        
        #print(f"from address = {addr}")
        #print("####################")
        handle_message(msg)


def handle_message(message):

    remoteMessage = json.loads(message)
    #print(f"{remoteMessage=}")
    #print(f"{current_process_info=}")
    remoteMessage['procInfo']['procAddr'] = tuple(remoteMessage['procInfo']['procAddr'])

    if remoteMessage["type"] == REQUEST:
        print(f"{Fore.YELLOW}Process {current_process_info['procPID']} got REQUEST message from {remoteMessage['procInfo']['procPID']}  {Fore.RESET}\n\n")
        if  current_process_info['procState'] == HELD or ( current_process_info["procTimestamp"] != None and
                remoteMessage["procInfo"]["procTimestamp"] > current_process_info["procTimestamp"] 
                and current_process_info["procState"] == WANTED
            ):
            
            #print(f"Deffered message of  {remoteMessage['procInfo']['procName']}")



            print(f"{Fore.RED}Putting in deferredQueue from {remoteMessage['procInfo']['procPID']} {Fore.RESET}\n\n")
            deferred_requests_queue[remoteMessage['procInfo']['procPID']] = remoteMessage['procInfo']['procAddr']
            #print(f"{deferred_requests_queue=}")

        else:
            message = {"type": REPLY, "procInfo": current_process_info}
            #print(f"Replied to {remoteMessage['procInfo']['procName']}")
            print(f"{Fore.GREEN}Sending reply message from {current_process_info['procPID']} to {remoteMessage['procInfo']['procName']} {Fore.RESET}\n\n")

            send_message(remoteMessage["procInfo"]["procAddr"], json.dumps(message))

    if remoteMessage['type'] == REPLY:
        print(f"{Fore.GREEN}Got REPLY message from {remoteMessage['procInfo']['procName']} {Fore.RESET}\n\n")
        reply_pending_queue.pop(remoteMessage["procInfo"]["procPID"])
        print(f"{reply_pending_queue=}")



def initialize_mutex(localAddr, procPID, procName, remoteAddr, numRemotes, self_socket):
    
    current_process_info["procName"], current_process_info["procPID"] = procName, procPID
    current_process_info["procState"] = RELEASED
    current_process_info["procAddr"], current_process_info["procRemotes"]  = tuple(localAddr), numRemotes
    
        

    #print(f"{current_process_info['procPID']} Initialization begin")
    
    global listening_socket
    listening_socket = self_socket


    for key, val in remoteAddr.items():
        remote_processes_addresses[key] = (val[0], val[1])
    
    
    msgThread = threading.Thread(target=thread_message_listener, args=(self_socket,))
    msgThread.start()

    #time.sleep(4)
    #print(f"{current_process_info['procPID']} Intialization done")


def lock_mutex():
    current_process_info["procState"] = WANTED

    current_process_info["procTimestamp"] = time.time()


    requestMessage = {
        "type": REQUEST,
        "procInfo": current_process_info
    }
    if(len(map_state) == 0): return False

    print("\n\n******************************************************************\n\n")
    print(f"{Fore.CYAN}Process {current_process_info['procPID']} wants to enter Critical Section {Fore.RESET}\n\n")

    print(f"{Fore.CYAN}Preparing to send request messages to all alive processes {Fore.RESET}\n\n")

    #print(f"{remote_processes_addresses=}")
    for key in remote_processes_addresses:
        if int(key) == int(current_process_info['procPID']) : continue

        #print(f"in enter_mutex {map_state=}")
        if int(key) in map_state:
            address = remote_processes_addresses[key]

            print(f"{Fore.RED}Sending request message from {current_process_info['procPID']} to {key} {Fore.RESET}\n\n")

            send_message(address, json.dumps(requestMessage))
            key=int(key)
            reply_pending_queue[key]=address
            #print(f"{reply_pending_queue=}")

       # else:
         #   print(f"Process {key} has failed so not sending request message")
            #print(f"{map_state=}")
    
    #print(f"{reply_pending_queue=}")

    while True:
        if len(reply_pending_queue) == 0:
            break
        else:
            counter=0
            reply_pending_queue_copy = reply_pending_queue.copy()
            while len(map_state) == 0:
                pass
            for key in reply_pending_queue_copy:
                if int(key) not in map_state:
                    print(f"{reply_pending_queue_copy=}")
                    print(f"{map_state=}")
                    counter+=1

                    if int(key) not in reply_pending_queue: continue

                    reply_pending_queue.pop(int(key))

    print(f"{Style.BRIGHT} {Fore.YELLOW} Entered CS {current_process_info['procPID']} {Style.RESET_ALL}\n\n")

    return True
    #print(f"{current_process_info['procPID']}Done lock_mutex")
    


def release_mutex():
    #print(f"{current_process_info['procPID']}In release_mutex\n")
    current_process_info['procState'] = RELEASED
    print(f"{Style.BRIGHT} {Fore.YELLOW} Exited CS {current_process_info['procPID']} {Style.RESET_ALL}\n\n")

    replyMessage = {"type": REPLY, "procInfo": current_process_info}
    
    
    #print(f"{reply_pending_queue=}")
    #print(f"{deferred_requests_queue=}")
    
    copy_def_q = deferred_requests_queue.copy()
    for key in list(copy_def_q):
    
        if int(key) in map_state:
            print(f"{Fore.GREEN}Sending deferred reply message from {current_process_info['procPID']} to {key} {Fore.RESET}\n\n")

            send_message(copy_def_q[key], json.dumps(replyMessage))
            #print(f"{deferred_requests_queue=}")
        deferred_requests_queue.pop(key)

    #print(f"{current_process_info['procPID']}Exit CS")
    return True



STATUS_CODES = [0,1,2,3,4]
REPLY, REQUEST, WANTED = STATUS_CODES[0], STATUS_CODES[1], STATUS_CODES[2]
HELD, RELEASED = STATUS_CODES[3], STATUS_CODES[4]

map_state = {}

def update_map_state():
    global map_state
    temp_map = dict()
    #map_state.clear()


    hb_ocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hb_ocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    hb_ocket.sendto("ALIVE_REQUEST".encode(), ("localhost", Live_checker_port))

    msg, addr = hb_ocket.recvfrom(MAX_CAPACITY)

    temp = json.loads(msg.decode())
    #print(f"in ra_Mtex {temp=}")

    # with open("alive.pkl","rb") as f:
    #     temp = pickle.load(f)

#beatDict={0: {'process_id': 0, 'port': 7485, 'msg_type': 'ZINDA', 'time_stamp': 1682156627.628755}, 1: {'process_id': 1, 'port': 7486, 'msg_type': 'ZINDA', 'time_stamp': 1682156627.7815492}}
    for k in temp:
        key = int(temp[k]['process_id'])
        value = int(temp[k]['port'])
    #print(f"{temp=}")
    # lines = f.readlines()
    # for line in lines:
    #     if len(line)>2:
    #         line = line.strip()
    #         line = line.split(",")
    #         key = (int)(line[0])
    #         value = (int)(line[1])
        #print(f"**************************Process {key} with {value} port alive*************************")
        temp_map[key] = value
    map_state = temp_map
    #print(f"in update_map_state {map_state=}")

def run_update_thread():
    while True:
        
        update_map_state()
        
        time.sleep(2)

thread = threading.Thread(target=run_update_thread)
thread.daemon = True
thread.start()


Live_checker_port = 2729
current_process_info = dict()

current_process_info['procName'] = None
current_process_info['procPID'] = None
current_process_info['procState'] = None
current_process_info['procTimestamp'] = None
current_process_info['procAddr'] = None
current_process_info['procRemotes'] = None

deferred_requests_queue, reply_pending_queue, remote_processes_addresses  = dict(), dict(), dict()

MAX_CAPACITY = 8192

