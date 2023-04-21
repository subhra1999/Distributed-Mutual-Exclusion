import sys, time, threading, socket, json, colorama
from colorama import Fore

# print(Fore.RED + 'This text is red in color')
# import cPickle as pickle


REPLY = 0
REQUEST = 1
WANTED = 2
HELD = 3
RELEASED = 4

# Stores the information of the local process
current_process_info = {
    'procName':         None,
    'procPID':          None,
    'procState':        None,
    'procTimestamp':    None,
    'procAddr':         None,
    'procRemotes':      None
}

deferred_requests_queue, reply_pending_queue, remote_processes_addresses  = list(), list(), dict()

MAXRECV = 8192
PRINT_LOG = True



def SendMessage(addr, message):
    if PRINT_LOG:
        print(f"{current_process_info['procPID']} Entering --> SendMessage\n")
    # if DEBUG:
    #     print(f"{localInfo['procPID']} Sending message --> {message['procInfo']['procName']}")
    sendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendingSocket.sendto(str(message).encode(), addr)
    sendingSocket.close()

    if PRINT_LOG:
        print(f'{current_process_info["procPID"]} Exiting --> SendMessage')
    return True


def MessageListener(listening_socket):
    

    while True:
        msg, addr = listening_socket.recvfrom(MAXRECV)
        msg = msg.decode()
        remoteMessage = json.loads(msg)
        print(f"{Fore.YELLOW} {current_process_info['procPID']} GOT MESSAGE in message listener from {remoteMessage['procInfo']['procPID']}  {Fore.RESET}")
        print(f"from address = {addr}")
        print("####################")
        MessageHandler(msg)


def MessageHandler(message):

    remoteMessage = json.loads(message)
    print(f"{remoteMessage=}")
    print(f"{current_process_info=}")
    remoteMessage['procInfo']['procAddr'] = tuple(remoteMessage['procInfo']['procAddr'])

    if remoteMessage["type"] == REQUEST:
        if  current_process_info['procState'] == HELD or ( current_process_info["procTimestamp"] != None and
                remoteMessage["procInfo"]["procTimestamp"] > current_process_info["procTimestamp"] 
                and current_process_info["procState"] == WANTED
            ):
            
            if PRINT_LOG:
                print(f"Deffered message from --> {remoteMessage['procInfo']['procName']}")
            
            print(f"{Fore.RED} putting in deferredQueue from {remoteMessage['procInfo']['procPID']} {Fore.RESET}")
            deferred_requests_queue.append(remoteMessage['procInfo']['procAddr'])
            print(f"{deferred_requests_queue=}")

        else:
            message = {"type": REPLY, "procInfo": current_process_info}
            if PRINT_LOG:
                print(f"Sent reply to --> {remoteMessage['procInfo']['procName']}")
            print(f"{Fore.GREEN} Sending reply message from {current_process_info['procPID']} to {remoteMessage['procInfo']['procName']} {Fore.RESET}")

            SendMessage(remoteMessage["procInfo"]["procAddr"], json.dumps(message))

    if remoteMessage['type'] == REPLY:
        if PRINT_LOG:
            print(f"{Fore.GREEN} Reply recieved from --> {remoteMessage['procInfo']['procName']} {Fore.RESET}")

            # print(f"Reply recieved from --> {remoteMessage['procInfo']['procName']}")
        reply_pending_queue.remove(remoteMessage["procInfo"]["procAddr"])




def initialize_mutex(localAddr, procPID, procName, remoteAddr, numRemotes, self_socket):
    # Initalize the local process info
    current_process_info["procName"] = procName
    current_process_info["procPID"] = procPID
    current_process_info["procState"] = RELEASED
    current_process_info["procAddr"] = tuple(localAddr)
    current_process_info["procRemotes"] = numRemotes
    
        

    if PRINT_LOG:
        print(f"{current_process_info['procPID']} Entering --> MutexInit\n")
    
    global listening_socket
    listening_socket = self_socket


    for key, val in remoteAddr.items():
        remote_processes_addresses[key] = (val[0], val[1])
    
    
    msgThread = threading.Thread(target=MessageListener, args=(self_socket,))
    msgThread.start()

    time.sleep(5)
    if PRINT_LOG:
        print(f"{current_process_info['procPID']} Exiting --> MutexInit\n----------------------------")


def lock_mutex():
    if PRINT_LOG:
        print(f"{current_process_info['procPID']} Entering --> MutexLock\n")
    current_process_info["procState"] = WANTED

    current_process_info["procTimestamp"] = time.time()


    requestMessage = {
        "type": REQUEST,
        "procInfo": current_process_info
    }

    for key in remote_processes_addresses:
        if int(key) == int(current_process_info['procPID']) : continue

        address = remote_processes_addresses[key]
        print(f"{Fore.RED} Sending request message from {current_process_info['procPID']} to {key} @ {current_process_info['procTimestamp']} {Fore.RESET}")

        SendMessage(address, json.dumps(requestMessage))
        reply_pending_queue.append(address)
        print(f"{reply_pending_queue=}")
    
    print(f"{reply_pending_queue}")

    while len(reply_pending_queue) > 0:
        pass

    print(f"{Fore.YELLOW} Entered CS {current_process_info['procPID']} {Fore.RESET}")

    if PRINT_LOG:
        print(f"{current_process_info['procPID']}Exiting  -->  MutexLock")
    return True


def release_mutex():
    if PRINT_LOG:
        print(f"{current_process_info['procPID']}Entering --> MutexUnlock\n")
    current_process_info['procState'] = RELEASED
    print(f"{Fore.YELLOW} Exited CS {current_process_info['procPID']} {Fore.RESET}")

    replyMessage = {"type": REPLY, "procInfo": current_process_info}
    
    
    print(f"{reply_pending_queue=}")
    print(f"{deferred_requests_queue=}")
    
    copy_def_q = deferred_requests_queue.copy()
    for address in copy_def_q:
        print(f"{Fore.GREEN} Sending deferred reply message from {current_process_info['procPID']} to {replyMessage['procInfo']['procName']} {Fore.RESET}")

        SendMessage(address, json.dumps(replyMessage))
        print(f"{deferred_requests_queue=}")
        deferred_requests_queue.remove(address)

    if PRINT_LOG:
        print(f"{current_process_info['procPID']}Exiting  --> MutexUnlock")
    return True


# def quit_mutex():
#     print(f"{Fore.RED}Exiting Mutex{Fore.RESET}")

