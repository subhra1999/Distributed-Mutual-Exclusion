import os, sys, time



server_port = int(sys.argv[1])
os.system(f"python3 server.py {server_port} 2 2 &")

time.sleep(5)
print("server started")


num_proc = 1
ports_begin = int(sys.argv[2])
process_ids = 0

def add_new_node(self_id):
    global ports_begin
    ports_begin += 1
    os.system(f"python3 process.py {self_id} {ports_begin} {server_port} &")
    return ports_begin


process_id_port = {}

for i in range(num_proc):
    print(f"num_proc={i}")
    process_id_port[process_ids] = add_new_node(i)
    process_ids += 1


