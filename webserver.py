import http.server
import socketserver
import threading

PORT = 80
DIRECTORY = "web"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_webserver():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

def run_in_thread(port=80,directory="web"):
    global PORT
    global DIRECTORY
    PORT = port
    DIRECTORY = directory
    webthread = threading.Thread(target=start_webserver)
    webthread.start()