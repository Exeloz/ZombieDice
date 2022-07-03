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

    players_path = ['stats/winner', 'stats/finalist-1', 'stats/finalist-3', 'stats/finalist-3']
    players = [IntelligentZombie(f'Jean-Claude-{i+1}', path, config_filename) for i, path in enumerate(players_path)]
    players += [GreedyZombie('Greedy')]    
    
    tournament = Tournament(players, n_players, 500, 
        gameClass=ZombieDiceGame, randomPlayerClass=RandomZombie,
        verbose=3)
    tournament.preleminary_selection(100)
    winners = tournament.play()
    ray.shutdown()

