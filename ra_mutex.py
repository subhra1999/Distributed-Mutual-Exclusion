import sys, time, threading, socket, json, colorama
from colorama import Fore

# print(Fore.RED + 'This text is red in color')
# import cPickle as pickle



def send_message(addr, message):
    print(f"{current_process_info['procPID']} sending message")
    sendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendingSocket.sendto(str(message).encode(), addr)
    sendingSocket.close()

    print(f'{current_process_info["procPID"]}  message sent')


def thread_message_listener(listening_socket):
    

    while True:
        msg, addr = listening_socket.recvfrom(MAX_CAPACITY)
        msg = msg.decode()
        remoteMessage = json.loads(msg)
        print(f"{Fore.YELLOW} {current_process_info['procPID']} GOT MESSAGE in message listener from {remoteMessage['procInfo']['procPID']}  {Fore.RESET}")
        print(f"from address = {addr}")
        print("####################")
        handle_message(msg)


def handle_message(message):

    remoteMessage = json.loads(message)
    print(f"{remoteMessage=}")
    print(f"{current_process_info=}")
    remoteMessage['procInfo']['procAddr'] = tuple(remoteMessage['procInfo']['procAddr'])

    if remoteMessage["type"] == REQUEST:
        if  current_process_info['procState'] == HELD or ( current_process_info["procTimestamp"] != None and
                remoteMessage["procInfo"]["procTimestamp"] > current_process_info["procTimestamp"] 
                and current_process_info["procState"] == WANTED
            ):
            
            print(f"Deffered message of  {remoteMessage['procInfo']['procName']}")
            
            print(f"{Fore.RED} putting in deferredQueue from {remoteMessage['procInfo']['procPID']} {Fore.RESET}")
            deferred_requests_queue[remoteMessage['procInfo']['procPID']] = remoteMessage['procInfo']['procAddr']
            print(f"{deferred_requests_queue=}")

        else:
            message = {"type": REPLY, "procInfo": current_process_info}
            print(f"Replied to {remoteMessage['procInfo']['procName']}")
            print(f"{Fore.GREEN} Sending reply message from {current_process_info['procPID']} to {remoteMessage['procInfo']['procName']} {Fore.RESET}")

            send_message(remoteMessage["procInfo"]["procAddr"], json.dumps(message))

    if remoteMessage['type'] == REPLY:
        print(f"{Fore.GREEN} Got reply from {remoteMessage['procInfo']['procName']} {Fore.RESET}")
        reply_pending_queue.pop(remoteMessage["procInfo"]["procPID"])




def initialize_mutex(localAddr, procPID, procName, remoteAddr, numRemotes, self_socket):
    
    current_process_info["procName"], current_process_info["procPID"] = procName, procPID
    current_process_info["procState"] = RELEASED
    current_process_info["procAddr"], current_process_info["procRemotes"]  = tuple(localAddr), numRemotes
    
        

    print(f"{current_process_info['procPID']} Initialization begin")
    
    global listening_socket
    listening_socket = self_socket


    for key, val in remoteAddr.items():
        remote_processes_addresses[key] = (val[0], val[1])
    
    
    msgThread = threading.Thread(target=thread_message_listener, args=(self_socket,))
    msgThread.start()

    time.sleep(5)
    print(f"{current_process_info['procPID']} Intialization done")


def lock_mutex():
    current_process_info["procState"] = WANTED

    current_process_info["procTimestamp"] = time.time()


    requestMessage = {
        "type": REQUEST,
        "procInfo": current_process_info
    }

    for key in remote_processes_addresses:
        if int(key) == int(current_process_info['procPID']) : continue

        if (int)(key) in map_state:
            address = remote_processes_addresses[key]

            print(f"{Fore.RED} Sending request message from {current_process_info['procPID']} to {key} @ {current_process_info['procTimestamp']} {Fore.RESET}")

            send_message(address, json.dumps(requestMessage))
            reply_pending_queue[(int)(key)]=address
            print(f"{reply_pending_queue=}")

        else:
            print(f"Process {key} has failed so not sending request message")
    
    print(f"{reply_pending_queue=}")

    while True:
        if len(reply_pending_queue) == 0:
            break
        else:
            counter=0
            for key in list(reply_pending_queue):
                if (int)(key) not in map_state:
                    counter+=1
            if counter == len(reply_pending_queue):
                break

    print(f"{Fore.YELLOW} Entered CS {current_process_info['procPID']} {Fore.RESET}")

    print(f"{current_process_info['procPID']}Done lock_mutex")
    return True


def release_mutex():
    print(f"{current_process_info['procPID']}In release_mutex\n")
    current_process_info['procState'] = RELEASED
    print(f"{Fore.YELLOW} Exited CS {current_process_info['procPID']} {Fore.RESET}")

    replyMessage = {"type": REPLY, "procInfo": current_process_info}
    
    
    print(f"{reply_pending_queue=}")
    print(f"{deferred_requests_queue=}")
    
    copy_def_q = deferred_requests_queue.copy()
    for key in list(copy_def_q):
    
        if (int)(key) in map_state:
            print(f"{Fore.GREEN} Sending deferred reply message from {current_process_info['procPID']} to {key} {Fore.RESET}")

            send_message(copy_def_q[key], json.dumps(replyMessage))
            print(f"{deferred_requests_queue=}")
        deferred_requests_queue.pop(key)

    print(f"{current_process_info['procPID']}Exit CS")
    return True



STATUS_CODES = [0,1,2,3,4]
REPLY, REQUEST, WANTED = STATUS_CODES[0], STATUS_CODES[1], STATUS_CODES[2]
HELD, RELEASED = STATUS_CODES[3], STATUS_CODES[4]

map_state = {}

def update_map_state():
    global map_state
    map_state.clear()
    with open("config.txt","r") as f:
        lines = f.readlines()
        for line in lines:
            if len(line)>2:
                line = line.strip()
                line = line.split(",")
                key = (int)(line[0])
                value = (int)(line[1])
                map_state[key] = value

def run_update_thread():
    while True:
        update_map_state()
        
        time.sleep(5)

thread = threading.Thread(target=run_update_thread)
thread.daemon = True
thread.start()

current_process_info = dict()

current_process_info['procName'] = None
current_process_info['procPID'] = None
current_process_info['procState'] = None
current_process_info['procTimestamp'] = None
current_process_info['procAddr'] = None
current_process_info['procRemotes'] = None

deferred_requests_queue, reply_pending_queue, remote_processes_addresses  = dict(), dict(), dict()

MAX_CAPACITY = 8192

