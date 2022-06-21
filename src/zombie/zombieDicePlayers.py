import os
import pickle

import neat
from src.neat.Genome.TournamentGenome import TournamentGenome
from src.neat.Reproduction.TournamentReproduction import TournamentReproduction
from src.neat.Stagnation.TournamentStagnation import TournamentStagnation
from src.base.player import Player, RandomPlayer
from src.zombie.zombieDiceGame import ZombieDiceType


class Zombie(Player):
    def __init__(self, name, decision_function):
        super().__init__(name, decision_function)
        self.brains = 0

    def get_brains(self):
        return self.brains

    def give_brains(self, brains):
        self.brains += brains

    def reset(self):
        super().reset()
        self.brains = 0

class GreedyZombie(Zombie):
    '''A player that keeps on rolling until it's too dagerous, meaning there is
    exactly 2 explosions on the board'''
    def __init__(self, name, limit=2):
        def decision_function(inputs, limit = limit, inputs_are_dice=13):
            n_explosions = sum([input == int(ZombieDiceType.explosion) for input in inputs[:inputs_are_dice]])
            return n_explosions < limit
        super().__init__(name, decision_function)

class SafeZombie(Zombie):
    '''A player that rolls until it has a brain. Stops right after, even if
    there is no explosion!'''
    def __init__(self, name, min=1, inputs_are_dice=13):
        def decision_function(inputs, min = min):
            n_brains = sum([input == int(ZombieDiceType.brain) for input in inputs[:inputs_are_dice]])
            return n_brains < min
        super().__init__(name, decision_function)

class StudentZombie(Zombie):
    '''A player that is learning.... scary!!'''
    def __init__(self, name, genome, config):
        
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome

        def decision_function(inputs):
            action = self.net.activate(inputs)[0]
            reroll = bool(round(min(1, max(0, action))))
            return reroll
        super().__init__(name, decision_function)

class IntelligentZombie(Zombie):
    '''A player governed by an AI!'''
    def __init__(self, name, player_path, config_path):
        with open(player_path, 'rb') as f:
            player = pickle.load(f)

        config = neat.Config(TournamentGenome, TournamentReproduction,
                            neat.DefaultSpeciesSet, TournamentStagnation,
                            config_path)
        self.net = neat.nn.FeedForwardNetwork.create(player, config)

        def decision_function(inputs):
            action = self.net.activate(inputs)[0]
            reroll = bool(round(min(1, max(0, action))))
            return reroll
        super().__init__(name, decision_function)

class RandomZombie(RandomPlayer, Zombie):
    def __init__(self, name, seed=None):
        super().__init__(name, seed)