"""Module that implements a datastructure
that is automatically synchronized to clients using websockets
"""

import threading
import asyncio
import websockets
import json

players_subscriptions = {}

database = {}

class DatabaseEntry:
    """Base database entry.
    Automatically propagates changes to all clients.

    Attributes
    ----------
    subscribers : set(websocket)
        clients that are subscribed to this entry and 
        will be notified of changes in value.
    value : anything
        the value of the entry
    path : string
        the path of this entry within the database
    """
    def __init__(self,value,path):
        """
        Parameters
        ----------
        value : anything
            initial value of the entry
        path : string
            the path of this entry within the database
        """
        self.subscribers = set()
        self.value = value
        self.path = path

    def get_value(self):
        """Get the value of this entry
        """
        return self.value

    async def handle_get(self, websocket):
        """Handle a get request from a connected client
        Parameters
        ----------
        websocket : websocket
            The client that made the request
        """
        await websocket.send(build_request("SET",self.path,self.get_value()))

    async def set_value(self, value):
        """Set the value of this entry
        Parameters
        ----------
        value : anything
            value to be set
        """
        self.value = value
        for websocket in self.subscribers:
            await websocket.send(build_request("SET",self.path,self.value))
        return self.value

    async def handle_set(self, value):
        """Handle a set request from a connected client
        Parameters
        ----------
        value : anything
            value to be set
        """
        await self.set_value(value)
        

    def subscribe(self, websocket):
        """Subscribe a client to changes in this entry
        Parameters
        ----------
        websocket : websocket
            The client that made the request
        """
        players_subscriptions[websocket].add(self)
        self.subscribers.add(websocket)
    
    def unsubscribe(self, websocket): 
        """Unsubscribe a client to changes in this entry
        Parameters
        ----------
        websocket : websocket
            The client that made the request
        """
        if self in players_subscriptions[websocket]:
            players_subscriptions[websocket].remove(self)
        self.subscribers.remove(websocket)

def create_entry(path,value,entry_type=DatabaseEntry):
    """Create a database entry of the given type
    Parameters
    ----------
    path : string
        path to this entry in the database
        the required tree structure will be created if it doesn't exist.
    value : anything
        initial value of this entry
    entry_type : type
        type of the entry (example : DatabaseEntry)
    """
    database[path] = entry_type(value,path)

def get_entry(path):
    """Look for the entry of a given path
    Parameters
    ----------
    path : string
        path to this entry in the database
    Returns
    -------
    DatabaseEntry : The entry that was found
    """
    if path != "" and path in current:
        return current[path]

def build_request(rtype, path, payload):
    """Build a huesync request
    Parameters
    ----------
    rtype : string
        The type of the request (GET, SET, SUB)
    path : string
        The path that the request refers to
    payload : anything
        The payload associated to the request
    Returns
    -------
    string, the built request
    """
    request_obj = {"type":rtype, "path":path, "payload":payload}
    return json.dumps(request_obj)

def parse_request(request):
    """Parse a huesync request into a python object
    Parameters
    ----------
    request : string
        The request in text format
    Returns
    -------
    (string, string, anything) : type, path and payload of the request
    """
    request_obj = json.loads(request)
    return (request_obj['type'], request_obj['path'], request_obj['payload'])

def register(websocket):
    """Register a client into the backend
    Parameters
    ----------
    websocket : websocket
        The client that connected
    """
    players_subscriptions[websocket] = set()

def unregister(websocket):
    """Unregister a client from the backend
    Parameters
    ----------
    websocket : websocket
        The client that disconnected
    """
    for subscription in players_subscriptions[websocket].copy():
        subscription.unsubscribe(websocket)
    del players_subscriptions[websocket]

async def handle_request(websocket, message):
    """Handle a client request assuming it is a huesync request
    Parameters
    ----------
    websocket : websocket
        The client that sent thed message
    message : string
        The message that the client sent. Must be a huesync request
    """
    rtype, path, payload = parse_request(message)
    if rtype == "GET":
        await traverse_database(path=path).handle_get(websocket)
    if rtype == "SUB":
        traverse_database(path=path).subscribe(websocket)
        await traverse_database(path=path).handle_get(websocket)
    if rtype == "SET":
        await traverse_database(path=path).handle_set(payload)

async def server(websocket, path):
    register(websocket)
    try:
        async for message in websocket:
            await handle_request(websocket, message)
    finally:
        unregister(websocket)

def run_server(host, port):
    """Run the huesync server. It will be started in an asyncio
    loop running in a separate thread.
    Parameters
    ----------
    host : string
        The host for the server (ip, etc)
    port : int
        The port for the server
    """
    start_server = websockets.serve(server, host, port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asthread = threading.Thread(target=asyncio.get_event_loop().run_forever)
    asthread.start()

def run_coro(coroutine):
    """Run a coroutine in the asyncio loop of the server.
    Use this to make huesync operations from outside the asyncio loop.
    Parameters
    ----------
    coroutine : asyncio coroutine
        coroutine to be run on the loop
    """
    asyncio.run_coroutine_threadsafe(coroutine,asyncio.get_event_loop())