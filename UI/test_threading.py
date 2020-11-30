import threading, queue, structs, time

data = structs.data()
data.queue = queue.Queue()


def parallel(d):
    counter = 0 
    while(True):
        d.queue.put(counter)
        counter+=1
        time.sleep(2)

t = threading.Thread(target=parallel,name="FPGA_SERIAL",args=[data],daemon=True)
t.start()

while(True):
    if(not data.queue.empty()):
        print(data.queue.get())
    else:
        # print("waiting")
        pass
