import os, sys, time



num_proc = int(sys.argv[1])
num_simulations = 2
server_port = int(sys.argv[2])

ports_begin = int(sys.argv[3])

os.system(f"python3 server.py {server_port} {num_proc} {num_simulations} &")

# time.sleep(5)
print("server started")


process_ids = 0

def add_new_node(self_id):
    global ports_begin
    os.system(f"gnome-terminal --title='{self_id}' -x bash -c 'python3 process.py {self_id} {ports_begin} {server_port}; exec bash'")
    # os.system(f"python3 process.py {self_id} {ports_begin} {server_port} &")
    ports_begin += 1
    return ports_begin


process_id_port = {}

for i in range(num_proc):
    print(f"num_proc={i}")
    process_id_port[process_ids] = add_new_node(i)
    process_ids += 1


