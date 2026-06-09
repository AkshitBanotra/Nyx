#!/usr/bin/env python3

import threading
import time

def worker_a():
    # runs simultaneously with worker_b
    print("Hello!")
    time.sleep(2)

def worker_b():
    # runs simuntaneously with worker_a
    print("Something!")

t1 = threading.Thread(target=worker_a)
t2 = threading.Thread(target=worker_b)

t1.start()      # worker_a starts running
t2.start()      # worker_b starts running simultaneously

#worker_a()
#worker_b()
