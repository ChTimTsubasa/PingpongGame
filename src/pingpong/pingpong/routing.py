from channels.routing import route, route_class
from channels.staticfiles import StaticFilesConsumer
from pingponggame.consumers import GameServer
from channels import include

game_routing = [
    route_class(GameServer, path = '^/(?P<room_id>[a-zA-Z0-9_]+)$')
]

channel_routing = [
    # Serve static files
    route('http.request', StaticFilesConsumer()),
]

routing = [
    # You can use a string import path as the first argument as well.
    include(game_routing, path = r'^/game'),
    include(channel_routing),
]
