from channels.routing import route
from pingponggame.consumers import ws_connect, ws_disconnect, ws_receive


channel_routing = [
    route('websocket.receive', ws_receive),
    # route('websocket.receive', ws_connect),
    # route('websocket.disconnect', ws_disconnect),
]