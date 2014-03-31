# coding: utf-8
import random
import sys

import core
from things import Player, Zombie, Box, Wall
from weapons import Rifle, Shotgun, Gun
from utils import astar, closest, distance, possible_moves


def min_heal_threshold(player):
    return player.MAX_LIFE - (player.MAX_LIFE / 10)

def max_heal_threshold(player):
    return player.MAX_LIFE - (player.MAX_LIFE / 4)

def distance_goal_fn(d):
    def distance_fn(self, other):
        return distance(self, other) < d
    return distance_fn

class Convi(Player):
    '''A player who heals based on convenience.'''

    def next_step(self, things, t):
        # action = random.choice(('move', 'attack', 'heal'))
        if self.life <= self.MAX_LIFE * .4: #max_heal_threshold(self):
            self.status = "I'm dieing!"
            return 'heal', self
        zombies = [thing for thing in things.values() if isinstance(thing, Zombie)]
        closest_zombie = closest(self, zombies)
        players = [thing for thing in things.values() if isinstance(thing, Player)]
        other_players = set(players) - set([self])
        zombie_locations = [position for position, thing in things if isinstance(thing, Zombie)]
        
        moves = possible_moves(self, things) 
        if moves and len([1 for move in moves if move in zombie_locations]) == 3:
            assert len(moves) == 1
            self.status = "I'm surrounded!"
            return 'move', moves[0]
        
        #if closest_zombie and len(list(filter(lambda z: distance(self, z) <= 3, zombies))) > 5:
        #    self.status = "I'm surrounded!"
        #    return 'attack', closest_zombie
        
        if other_players and closest_zombie and len(list(filter(lambda z: distance(self, z) <= closest_zombie.weapon.max_range, zombies))) > 1:
            avgx = int(sum(player.position[0] for player in other_players) / len(other_players))
            avgy = int(sum(player.position[0] for player in other_players) / len(other_players))
            moves = astar(self.position, (avgx, avgy), closed=set(things.keys()) - set([(avgx, avgy)]), goal_met=distance_goal_fn(core.HEALING_RANGE))
            if moves:
                self.status = 'This is a little overwhelming'
                return 'move', moves[0]
                
        
        players.sort(key=lambda x: x.life)

        if closest_zombie:
            moves_left_predicted = distance(self, closest_zombie) - closest_zombie.weapon.max_range #self.weapon.max_range
        else:
            moves_left_predicted = 9999

        if moves_left_predicted - 1 > 0:
            if not closest_zombie:
                players_to_heal = players
            else:
                players_to_heal = list(filter(lambda p: (distance(self, p) - core.HEALING_RANGE) < moves_left_predicted, players))
            if players_to_heal:
                player_to_heal = players_to_heal[0]
                if player_to_heal.life <= max_heal_threshold(self):
                    self.status = 'healing ' + player_to_heal.name
                    if distance(self, player_to_heal) < core.HEALING_RANGE:
                        return 'heal', player_to_heal
                    else:
                        moves = astar(self.position, player_to_heal.position, closed=things.keys(), goal_met=distance_goal_fn(core.HEALING_RANGE))
                        if moves:
                            return 'move', moves[0]
                        else:
                            self.status = "Healing (can't reach " + player_to_heal.name + ')'
                            return 'heal', self
                else:
                    if self.life < min_heal_threshold(self):
                        self.status = "Nobody makes me bleed my own blood!"
                        return 'heal', self
                    else:
                        self.status = "If it bleeds, we can kill it..."
                        if closest_zombie and distance(self, closest_zombie) <= self.weapon.max_range:
                            return 'attack', closest_zombie
                        else:
                            if closest_zombie:
                                moves = astar(self.position, closest_zombie.position, closed=things.keys(), goal_met=distance_goal_fn(self.weapon.max_range))
                            else:
                                moves = []
                            if moves:
                                return 'move', moves[0]
                            else:
                                self.status = "Healing (can't attack)"
                                return 'heal', self

            else:
                if self.life < min_heal_threshold(self):
                    self.status = "Nobody makes me bleed my own blood!"
                    return 'heal', self
                else:
                    self.status = "WE'RE INVINCIBLE!"
                    if closest_zombie and distance(self, closest_zombie) <= self.weapon.max_range:
                        return 'attack', closest_zombie
                    else:
                        if closest_zombie:
                            moves = astar(self.position, closest_zombie.position, closed=things.keys(), goal_met=distance_goal_fn(self.weapon.max_range))
                        else:
                            moves = []
                        if moves:
                            return 'move', moves[0]
                        else:
                            self.status = "Healing (can't attack)"
                            return 'heal', self
        else:
            self.status = "DIE!"
            return 'attack', closest_zombie


def create(rules, objectives=None):
    icon, weapon = random.choice([('S', Shotgun()), ('R', Rifle()), ('G', Gun())])
    return Convi('convi', 'red', rules=rules, weapon=weapon, icon=icon, objectives=objectives)

#def breadth_first(start, goal_met, closed=[], 