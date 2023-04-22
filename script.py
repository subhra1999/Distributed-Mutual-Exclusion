import os, sys, time



num_simulations = int(sys.argv[1])
server_port = int(sys.argv[2])
ports_begin = int(sys.argv[3])
num_proc = int(input("How many nodes you want to start with: "))

with open("config.txt", "w") as f:
    f.write("")

# os.system(f"python3 server.py {server_port} {num_proc} {num_simulations} &")
os.system(f"gnome-terminal --title='Server' -x bash -c 'python3 server.py {server_port} {num_proc} {num_simulations} ; exec bash'")

# time.sleep(5)
print("server started")


process_ids = 0

def add_new_node(self_id):
    global ports_begin
    time.sleep(1)
    os.system(f"gnome-terminal --title='{self_id}' -x bash -c 'python3 process.py {self_id} {ports_begin} {server_port} {num_simulations}; exec bash'")
    # os.system(f"python3 process.py {self_id} {ports_begin} {server_port} &")
    ports_begin += 1
    return ports_begin


process_id_port = {}



for i in range(num_proc):
    print(f"num_proc={i}")
    process_id_port[process_ids] = add_new_node(i)
    process_ids += 1


while True:
    resp = input("Do you want to add new node: (y/[n]): ")
    if(resp == "y"):
        print(f"num_proc={i}")
        i += 1
        process_id_port[process_ids] = add_new_node(i)
        process_ids += 1
    elif resp == "n":
        break
    else:
        print("Give valid input: (y/[n])")
