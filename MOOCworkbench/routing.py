from channels.routing import route

from experiments_manager.consumers import ws_connect

channel_routing = [
    route("websocket.connect", ws_connect),
]