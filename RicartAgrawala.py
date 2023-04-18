import sys
import time
import threading
import socket
import json
import colorama
from colorama import Fore

# print(Fore.RED + 'This text is red in color')
# import cPickle as pickle

##################################################################################################################################
# Variabel declarations                                                                                                         #
##################################################################################################################################
REPLY = 0
REQUEST = 1
WANTED = 0
HELD = 1
RELEASED = 2

# Stores the information of the local process
localInfo = {
    'procName':         None,
    'procPID':          None,
    'procState':        None,
    'procTimestamp':    None,
    'procAddr':         None,
    'procRemotes':      None
}

defferedQueue = []  # Waiting to reply too
replyQueue = []  # Awaiting replies from
msgThread = None

remoteAddresses = {}  # Store the addresses of the other processes

MAXRECV = 4096
DEBUG = True

# listening_socket = None

##################################################################################################################################
# Auxillary functions                                                                                                            #
##################################################################################################################################


def MutexInit(localAddr, procPID, procName, remoteAddr, remoteName, numRemotes, self_socket):
    # Initalize the local process info
    localInfo["procName"] = procName
    localInfo["procPID"] = procPID
    localInfo["procState"] = RELEASED
    localInfo["procAddr"] = tuple(localAddr)
    localInfo["procRemotes"] = numRemotes
    # localInfo["procTimestamp"] 
    # localInfo["self_socket"] = self_socket

    # print(f"{remoteAddr=}")

    # remoteAddresses = 
    # for key in remoteAddr:
    #     remoteAddresses.
        

    if DEBUG:
        print(f"{localInfo['procPID']} Entering --> MutexInit\n")
    
    global listening_socket
    listening_socket = self_socket

    # print(f"{localInfo=}")

    # splitting the remoteAddr and remoteName tuples into separate variables
    # remoteAddr1, remoteAddr2 = remoteAddr
    # remoteName1, remoteName2 = remoteName  # Don't know if we need this

    # Add the other two processes addresses to a dictionary for access later
    # remoteAddresses[remoteName1] = remoteAddr1
    # remoteAddresses[remoteName2] = remoteAddr2

    for key, val in remoteAddr.items():
        remoteAddresses[key] = (val[0], val[1])
    
    # print(f"{remoteAddresses=}")

    # global remoteAddresses
    # remoteAddresses = remoteAddr
    # Create thread that is supposed to fork the messageListener function to run in the background
    msgThread = threading.Thread(target=MessageListener, args=(self_socket,))
    msgThread.start()

    time.sleep(5)
    if DEBUG:
        print(f"{localInfo['procPID']} Exiting --> MutexInit\n----------------------------")


##################################################################################################################################
# Messaging Functions                                                                                                          #
##################################################################################################################################
def SendMessage(addr, message):
    if DEBUG:
        print(f"{localInfo['procPID']} Entering --> SendMessage\n")
    # if DEBUG:
    #     print(f"{localInfo['procPID']} Sending message --> {message['procInfo']['procName']}")
    sendingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendingSocket.sendto(str(message).encode(), addr)
    sendingSocket.close()

    if DEBUG:
        print(f'{localInfo["procPID"]} Exiting --> SendMessage')
    return True


def MessageListener(listening_socket):
    # listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the local address
    # listeningSocket.bind(localInfo['procAddr'])
    # global listening_socket

    while True:
        msg, addr = listening_socket.recvfrom(MAXRECV)
        msg = msg.decode()
        remoteMessage = json.loads(msg)
        print(f"{Fore.YELLOW} {localInfo['procPID']} GOT MESSAGE in message listener from {remoteMessage['procInfo']['procPID']}  {Fore.RESET}")
        print(f"from address = {addr}")
        print("####################")
        print("####################")
        # print(f"received_messgae = {msg}")
        MessageHandler(msg)


def MessageHandler(message):
    # Convert the string we get back to a dictionary
    

    remoteMessage = json.loads(message)
    print(f"{remoteMessage=}")
    print(f"{localInfo=}")
    remoteMessage['procInfo']['procAddr'] = tuple(remoteMessage['procInfo']['procAddr'])

    if remoteMessage["type"] == REQUEST:
        if  localInfo['procState'] == HELD or ( localInfo["procTimestamp"] != None and
                remoteMessage["procInfo"]["procTimestamp"] > localInfo["procTimestamp"] 
                and localInfo["procState"] == WANTED
            ):
            
            if DEBUG:
                print(f"Deffered message from --> {remoteMessage['procInfo']['procName']}")
            
            print(f"{Fore.RED} putting in deferredQueue from {remoteMessage['procInfo']['procPID']} {Fore.RESET}")
            defferedQueue.append(remoteMessage['procInfo']['procAddr'])
            print(f"{defferedQueue=}")

        else:
            message = {"type": REPLY, "procInfo": localInfo}
            if DEBUG:
                print(f"Sent reply to --> {remoteMessage['procInfo']['procName']}")
            print(f"{Fore.GREEN} Sending reply message from {localInfo['procPID']} to {remoteMessage['procInfo']['procName']} {Fore.RESET}")

            SendMessage(remoteMessage["procInfo"]["procAddr"], json.dumps(message))

    if remoteMessage['type'] == REPLY:
        if DEBUG:
            print(f"{Fore.GREEN} Reply recieved from --> {remoteMessage['procInfo']['procName']} {Fore.RESET}")

            # print(f"Reply recieved from --> {remoteMessage['procInfo']['procName']}")
        replyQueue.remove(remoteMessage["procInfo"]["procAddr"])

##################################################################################################################################
# Mutex Functions                                                                                                               #
##################################################################################################################################


def MutexLock(the_mutex):
    if DEBUG:
        print(f"{localInfo['procPID']} Entering --> MutexLock\n")
    localInfo["procState"] = WANTED  # Change state
    # Generate the timestamp for the message
    localInfo["procTimestamp"] = time.time()


    requestMessage = {"type": REQUEST,
                      "procInfo": localInfo, "mutex": the_mutex}

    # If we can't send any messages we assume that we are first and therefore can enter the section without any replies
    
    for key in remoteAddresses:
        if int(key) == int(localInfo['procPID']) : continue

        address = remoteAddresses[key]
        # print(Fore.RED + 'Sending request message' + Fore.RESET)
        print(f"{Fore.RED} Sending request message from {localInfo['procPID']} to {key} @ {localInfo['procTimestamp']} {Fore.RESET}")

        SendMessage(address, json.dumps(requestMessage))
        # Only add addresses to the replyQueue if we sent a request to someone.
        replyQueue.append(address)
        print(f"{replyQueue=}")
    
    print(f"{replyQueue}")

    while len(replyQueue) > 0:
        # print(f"{len(replyQueue)=} in {localInfo['procPID']=}")
        pass  # Wait for the replyQueue to empty before continuing

    print(f"{Fore.YELLOW} Entered CS {localInfo['procPID']} {Fore.RESET}")

    if DEBUG:
        print(f"{localInfo['procPID']}Exiting  -->  MutexLock")
    return True


def MutexUnlock(the_mutex):
    if DEBUG:
        print(f"{localInfo['procPID']}Entering --> MutexUnlock\n")
    localInfo['procState'] = RELEASED
    print(f"{Fore.YELLOW} Exited CS {localInfo['procPID']} {Fore.RESET}")

    replyMessage = {"type": REPLY, "procInfo": localInfo, "mutex": the_mutex}
    
    
    print(f"{replyQueue=}")
    print(f"{defferedQueue=}")
    
    copy_def_q = defferedQueue.copy()
    for address in copy_def_q:
        # print(Fore.GREEN + 'Sending reply message' + Fore.RESET)
        print(f"{Fore.GREEN} Sending deferred reply message from {localInfo['procPID']} to {replyMessage['procInfo']['procName']} {Fore.RESET}")

        SendMessage(address, json.dumps(replyMessage))
        print(f"{defferedQueue=}")
        defferedQueue.remove(address)

    if DEBUG:
        print(f"{localInfo['procPID']}Exiting  --> MutexUnlock")
    return True


def MutexExit():
    return True
