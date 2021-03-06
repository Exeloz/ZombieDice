import os
import pickle
import sys
import ray
import numpy as np
from matplotlib import pyplot as plt

import neat
import src.zombie.zombieDiceGame
from evolve import ZombieEvaluator, ZombieEvolver

if __name__ == '__main__':
    from os import listdir
    from os.path import isfile, join

    if len(sys.argv) > 1:
        num_cpus = int(sys.argv[1])
    else:
        num_cpus = 4

    ray.init(num_cpus=num_cpus)

    n_players = 4
    config_filename = f'configs/config-{n_players}-players'
    evaluator = ZombieEvaluator(n_players, 5000, 40000, verbose=True)

    to_load = [f'to_load/{f}' for f in listdir('to_load/') if isfile(join('to_load/', f))]
    genomes = [ZombieEvaluator.load_genome(g, id+1) for id, g in enumerate(to_load)]
    evaluator.eval_genomes_tournament(genomes, ZombieEvolver.load_config(config_filename))
    ray.shutdown()

