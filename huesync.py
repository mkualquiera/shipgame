"""
    Bootleg version of Huesync by: mkualquiera
    written by: nexustix
"""

import websockets
import asyncio
import threading
import json

def build_request(rtype, path, payload):
    """Turn arguments into websocket request

    Args:
        rtype (str): response type
        path (str): path
        payload (str): payload
    """
    request_obj = {"type":rtype, "path":path, "payload":payload}
    return json.dumps(request_obj)

def parse_request(request):
    """Split websocket request into relevant elements

    Args:
        websocket (Websocket): the websocket

    Returns:
        (str): response type
        (str): path
        (str): payload
    """
    request_obj = json.loads(request)
    return (request_obj['type'], request_obj['path'], request_obj['payload'])

class DatabaseEntry:

    def __init__(self,value,path):
        self.subscribers = set()
        self.value = value
        self.path = path

    def get_value(self):
        """Get contained value

        Returns:
            (any): contained value
        """
        return self.value

    async def set_value(self, value):
        """Set contained value

        Args:
            (any): value to be contained
        """
        self.value = value
        for websocket in self.subscribers:
            await websocket.send(build_request("SET",self.path,self.value))
        return self.value

    async def handle_get(self, websocket):
        """Handle websocket get request

        Args:
            websocket (Websocket): the websocket
        """
        await websocket.send(build_request("SET",self.path,self.get_value()))

    async def handle_set(self, value):
        """Handle websocket set request

        Args:
            value (any): value to set
        """
        await self.set_value(value)

    def add_subscription(self, websocket):
        """Add subscriver to entry

        Args:
            websocket (Websocket): new subscriber
        """
        self.subscribers.add(websocket)

    def remove_subscription(self, websocket):
        """Remove subscriver from entry

        Args:
            websocket (Websocket): subscriber to remove
        """
        self.subscribers.remove(websocket)


class HueSync():
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self.loop = None
        self._data = {}
        self._players_subscriptions = {}

    def create_entry(self, path, value, entry_type=DatabaseEntry):
        """Create new database entry

        Args:
            path (str): key of the value
            value (any): value of the entry
            entry_type (class): class to use to contain the value
        """
        self._data[path] = entry_type(value,path)

    def get_entry(self, path=""):
        """Retrieve value from database

        Args:
            path (str): key of the value

        Returns:
            (any): value found
        """
        if path != "" and path in self._data:
            return self._data[path]

    def _register(self, websocket):
        self._players_subscriptions[websocket] = set()

    def _unregister(self, websocket):
        for subscription in self._players_subscriptions[websocket].copy():
            subscription.remove_subscription(websocket)
        del self._players_subscriptions[websocket]

    def subscribe_client(self, client, entry):
        """Subscribe client to a given entry

        Args:
            client (Websocket): the client
            entry (DatabaseEntry): the entry
        """
        self._players_subscriptions[client].add(entry)
        entry.add_subscription(client)

    def unsubscribe_client(self, client, entry):
        """Unsubscribe client from a given entry

        Args:
            client (Websocket): the client
            entry (DatabaseEntry): the entry
        """
        if entry in self._players_subscriptions[client]:
            self._players_subscriptions[client].remove(entry)
        entry.remove_subscription(client)

    async def _handle_request(self, websocket, message):
        rtype, path, payload = parse_request(message)
        print("HUESYNC", rtype, path, payload)
        if rtype == "GET":
            await self.get_entry(path=path).handle_get(websocket)
        if rtype == "SUB":
            self.subscribe_client(websocket, self.get_entry(path=path))
            await self.get_entry(path=path).handle_get(websocket)
        if rtype == "SET":
            await self.get_entry(path=path).handle_set(payload)

    async def _server_work(self, websocket, path):
        self._register(websocket)
        try:
            async for message in websocket:
                await self._handle_request(websocket, message)
        finally:
            self._unregister(websocket)
    
    def run_coro(self, coroutine):
        """Run a coroutine in the asyncio loop of the server.
        Use this to make huesync operations from outside the asyncio loop.
        Args:
            client (_FutureT[_T]): coroutine to be executed
        """
        asyncio.run_coroutine_threadsafe(coroutine,self.loop)

    def run_server(self):
        """Start the server in a new thread
        """
        def run():
            loop = asyncio.new_event_loop()
            self.loop = loop
            asyncio.set_event_loop(loop)

            start_server = websockets.serve(self._server_work, self._host, self._port)
            loop.run_until_complete(start_server)

            loop.run_forever()

        threading.Thread(target=run).start()
