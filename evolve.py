import multiprocessing
import os
import pickle
import math
import numpy as np
import neat
import visualize

from zombieDicePlayers import StudentZombie, RandomZombie
from zombieDiceGame import ZombieDiceGame
from tournament import Tournament

number_games = 1000
stats_location = 'stats'

def eval_genome(zombie):
    return zombie.get_tournament_position()

def eval_genomes(genomes, config):
    zombies = [StudentZombie(f'Student-{genome_id}', genome, config) 
                    for genome_id, genome in genomes]
    tournament = Tournament(zombies, 4, number_games, ZombieDiceGame, RandomZombie)
    tournament.preleminary_selection()
    w = tournament.play()
    for zombie in zombies:
        zombie.genome.fitness = eval_genome(zombie)

def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))
    winner = p.run(eval_genomes, 1000)

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
    run()
