from pingponggame.models import *
from django.core.cache import cache

class GameCache():

    @staticmethod
    def init_game(game):
        players = game.player_set.all()
        user_list = []
        for player in players:
            user = player.user
            user_list.append(user)
            cache.set(user, game)
        cache.set(game, user_list)

    @staticmethod
    def delete_game(game):
        user_list = cache.get(game)
        for user in user_list:
            cache.remove(user)
        cache.remove(game)

    @staticmethod
    def get_opponents(user):
        game = cache.get(user)
        user_list = cache.get(game)
        user_list.remove(user)
        return user_list
    
    @staticmethod
    def get_users(game):
        return cache.get(game)

    @staticmethod
    def get_oppo_group(player_id):
        oppo_user_id = cache.get(str(user_id) + OPPO_SUF)
        return cache.get(CHANNEL_PRE + str(oppo_user_id))

