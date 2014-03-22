# coding: utf-8
from game import Rules
from utils import closest, distance


class EvacuationRules(Rules):
    '''A kind of game where players must get together to be evacuated.

       Team wins when all alive players are at 2 or less distance from another
       alive player, and at least half of the team must survive.
    '''
    def get_alive_players(self):
        '''Get the alive players.'''
        return [player for player in self.game.players
                if player.life > 0]

    def alive_players_together(self):
        '''Are the alive players together (close to each other)?'''
        alive_players = self.get_alive_players()

        # the logic is this: the area must be at most, 3 * alive players
        positions = [player.position for player in alive_players]
        xs, ys = zip(*positions)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        area = (max_x - min_x) * (max_y - min_y)

        return area <= len(alive_players) * 3


    def half_team_alive(self):
        '''At least half of the original team alive?'''
        alive_players = self.get_alive_players()
        return len(alive_players) >= len(self.game.players) / 2

    def game_ended(self):
        '''Has the game ended?'''
        if self.half_team_alive():
            return self.alive_players_together()
        else:
            return True

    def game_won(self):
        '''Was the game won?'''
        if self.half_team_alive():
            return True, u'players got together and were evacuated :)'
        else:
            return False, u'too few survivors to send a rescue helicopter :('


def create(game):
    return EvacuationRules(game)
