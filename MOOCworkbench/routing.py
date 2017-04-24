from channels.routing import route

from experiments_manager.consumers import connect_worker_output
from experiments_manager.consumers import disconnect_worker_output

channel_routing = [
    route("websocket.connect", connect_worker_output, path=r"^/experiments/(?P<worker>[a-zA-Z0-9_]+)/$"),
    route("websocket.disconnect", disconnect_worker_output),
]