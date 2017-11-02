from channels.routing import route
from pingponggame.consumers import ws_add, ws_disconnect, ws_message


channel_routing = [
    route('websocket.connect', ws_add),
    route('websocket.receive', ws_message),
    route('websocket.disconnect', ws_disconnect),
]