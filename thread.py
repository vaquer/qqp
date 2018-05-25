import threading
import requests
import queue
from collections import deque

# qe = deque()
qe = queue.Queue()
# called by each thread
def get_url(q, url):
    q.put(requests.get(url).text)

theurls = ["http://google.com", "http://yahoo.com"]


for u in theurls:
    t = threading.Thread(target=get_url, args = (qe,u))
    t.daemon = True
    t.start()
    t.join()

# s = q.get()
print (qe)