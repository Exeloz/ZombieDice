import os
import pickle
import sys
import ray
import numpy as np
from matplotlib import pyplot as plt

from src.base.tournament import Tournament
from src.zombie.zombieDicePlayers import *
from evolve import ZombieEvaluator, ZombieEvolver
from src.zombie.zombieDiceGame import ZombieDiceGame

if __name__ == '__main__':

    if len(sys.argv) > 1:
        num_cpus = int(sys.argv[1])
    else:
        num_cpus = 4

    ray.init(num_cpus=num_cpus)

    n_players = 4
    config_filename = f'configs/config-{n_players}-players'

    player_path = 'stats/winner-4-player'
    players = [GreedyZombie('Grinch'), RandomZombie('Randall'), SafeZombie('Kyle'),
        IntelligentZombie('Jean-Claude', player_path, config_filename)]
        
    tournament = Tournament(players, n_players, 1000000, 
        gameClass=ZombieDiceGame, randomPlayerClass=RandomZombie,
        verbose=2)
    tournament.preleminary_selection(0)
    winners = tournament.play()
    ray.shutdown()

