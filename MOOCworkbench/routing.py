from channels.routing import route
from UserManager.consumers import *
from channels import include

channel_routing = [
    route("websocket.connect", ws_add, path=r"^/(?P<room>[a-zA-Z0-9_]+)/$"),
    route("websocket.receive", ws_message),
    route("websocket.disconnect", ws_disconnect),
]