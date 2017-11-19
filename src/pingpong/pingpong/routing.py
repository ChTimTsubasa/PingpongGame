from channels.routing import route, route_class
from pingponggame.consumers import GameServer
from channels import include

game_routing = [
    route_class(GameServer, path = '^/(?P<room_id>[a-zA-Z0-9_]+)$')
]

routing = [
    # You can use a string import path as the first argument as well.
    include(game_routing, path = r'^/game'),
]
