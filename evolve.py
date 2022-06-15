import math
import multiprocessing
import os

import ray
import pickle
from pathlib import Path

import numpy as np

import neat
import src.neat.visualize as visualize
from src.base.tournament import Tournament
from src.zombie.zombieDiceGame import ZombieDiceGame
from src.zombie.zombieDicePlayers import (GreedyZombie, RandomZombie,
                                          StudentZombie)

number_games = 500
number_gens = 100
stats_location = 'stats'
genome_locations = 'checkpoints'
current_gen = 0

def eval_genome(zombie, previous_winner):
    if previous_winner is None:
        previous_winner_fitness = 0
    else:
        previous_winner_fitness = previous_winner.get_tournament_position()
    fitness = max(0, zombie.get_tournament_position() - previous_winner_fitness)
    if previous_winner is not None and zombie.name == previous_winner.name:
        fitness = 0.5
    return fitness

def eval_genomes(genomes, config):
    previous_best_id = find_best_genome(genomes)
    zombies = [StudentZombie(create_zombie_name(genome_id), genome, config) 
                    for genome_id, genome in genomes]
    tournament = Tournament(zombies, 4, number_games, 
        gameClass=ZombieDiceGame, randomPlayerClass=RandomZombie)
    tournament.preleminary_selection()
    winners = tournament.play()

    if previous_best_id is None:
        previous_winner = None
    else:
        previous_winner = find_zombie(zombies, previous_best_id)
    
    for zombie in zombies:
        zombie.genome.fitness = eval_genome(zombie, previous_winner)

    checkpoint(genomes)
    return winners

def create_zombie_name(genome_id):
    return f'Student-{genome_id}'

def find_zombie(zombies, genome_id):
    for zombie in zombies:
        if str(zombie) == create_zombie_name(genome_id):
            return zombie 

def find_best_genome(genomes):
    genomes_light = [(g_id, g.fitness) for g_id, g in genomes if g.fitness is not None]
    if len(genomes_light) == 0:
        return None
    max_id = max(genomes_light, key=lambda g: g[1])[0]
    for genome_id, _ in genomes:
        if genome_id == max_id:
            return genome_id

def checkpoint(genomes):
    global current_gen
    directory_path = Path(f"{genome_locations}/gen{current_gen}")
    for genome_id, genome in genomes:
        path = Path.joinpath(directory_path, str(genome_id))
        directory_path.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(genome, f)
    current_gen += 1

def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'configs/config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1, filename_prefix=Path(f"{genome_locations}/neat/neat-checkpoint")))
    winner = p.run(eval_genomes, number_gens)

    # Save the winner.
    with open(f"{stats_location}/winner-feedforward", 'wb') as f:
        pickle.dump(winner, f)

    print(winner)

    visualize.plot_stats(stats, ylog=True, view=True, filename=f"{stats_location}/feedforward-fitness.svg")
    #visualize.plot_species(stats, view=True, filename=f"{stats_location}/feedforward-speciation.svg")

    node_names = {-1: 'easy1', -2: 'easy2', -3: 'easy3', 
        -4: 'easy4', -5: 'easy5', -6: 'easy6', 
        -7: 'mod1', -8: 'mod2', -9: 'mod3', -10: 'mod4', 
        -11: 'hard1', -12: 'hard2', -13: 'hard3', 
        0: 'reroll'}
    visualize.draw_net(config, winner, True, node_names=node_names)

    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename=f"{stats_location}/winner-feedforward.gv")
    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename=f"{stats_location}/winner-feedforward-enabled-pruned.gv", prune_unused=True)

if __name__ == '__main__':
    ray.init(num_cpus=4)
    run()
    ray.shutdow()
