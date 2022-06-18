import os
import pickle
import sys
import numpy as np
from matplotlib import pyplot as plt

import neat
import src.zombie.zombieDiceGame
from evolve import ZombieEvolver

if __name__ == '__main__':
    from os import listdir
    from os.path import isfile, join

    if len(sys.argv) > 1:
        num_cpus = int(sys.argv[1])
    else:
        num_cpus = 4
    n_players = 4
    config_filename = f'configs/config-{n_players}-players'
    evolve = ZombieEvolver(config_filename, n_gens=1000, n_against=n_players, n_cpus=num_cpus)
    restore_point = 'checkpoints/neat/neat-checkpoint287'
    evolve.init_population()

    to_load = [f'to_load/{f}' for f in listdir('to_load/') if isfile(join('to_load/', f))]
    evolve.add_genomes(to_load)
    _ = evolve.run()
