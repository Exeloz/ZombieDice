from player import Player
from zombieDiceGame import ZombieDiceType
import pickle
import neat
import os

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
        def decision_function(inputs, limit = limit):
            n_explosions = sum([input == int(ZombieDiceType.explosion) for input in inputs])
            return n_explosions < limit
        super().__init__(name, decision_function)

class SafeZombie(Zombie):
    '''A player that rolls until it has a brain. Stops right after, even if
    there is no explosion!'''
    def __init__(self, name, min=1):
        def decision_function(inputs, min = min):
            n_brains = sum([input == int(ZombieDiceType.brain) for input in inputs])
            return n_brains < min
        super().__init__(name, decision_function)

class IntelligentZombie(Zombie):
    '''A player governed by an AI!'''
    def __init__(self, name, player_path, config_path):
        with open(player_path, 'rb') as f:
            player = pickle.load(f)

        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation,
            config_path)
        self.net = neat.nn.FeedForwardNetwork.create(player, config)

        def decision_function(inputs):
            action = self.net.activate(inputs)[0]
            reroll = bool(round(min(1, max(0, action))))
            return reroll
        super().__init__(name, decision_function)