import os
import threading

def server_thread_func():
    os.system("python server.py")

def bot_thread_func():
    os.system("python main.py")

server_thread = threading.Thread(target=server_thread_func)
bot_thread = threading.Thread(target=bot_thread_func)

server_thread.start()
bot_thread.start()