from channels.routing import route
from pingponggame.consumers import ws_add, ws_disconnect, ws_message


channel_routing = [
	#When user open gameroom.html
    route('websocket.connect', ws_add, path='^/(?P<room_id>[a-zA-Z0-9_]+)$'),
    route('websocket.receive', ws_message, path='^/(?P<room_id>[a-zA-Z0-9_]+)$'),
    route('websocket.disconnect', ws_disconnect, path='^/(?P<room_id>[a-zA-Z0-9_]+)$'),
]
