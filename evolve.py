"""
Single-pole balancing experiment using a feed-forward neural network.
"""

import multiprocessing
import os
import pickle
import math
import numpy as np

import zombieDiceGame
import neat
import visualize

runs_per_net = 100

# Use the NN network phenotype and the discrete actuator force function.
def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    fitnesses = []

    for runs in range(runs_per_net):
        game = zombieDiceGame.ZombieDiceGame()

        # Run the given simulation for up to num_steps time steps.
        fitness = 0.0
        reroll = True
        while reroll:
            inputs = game.get_stale_state()
            action = net.activate(inputs)[0]

            # Do we reroll?
            reroll = bool(round(min(1, max(0, action))))
            if reroll: 
                game.roll()

            # Stop if the to many explosions occured of if all dice are used and
            # no rerolls can be achieved
            if game.turn_ended():
                reroll = False

            fitness = game.get_points()

        fitnesses.append(fitness)

    # The genome's fitness is its average performance across all runs.
    return np.average(fitnesses)


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    winner = pop.run(pe.evaluate, n=5000)

    # Save the winner.
    with open('stats/winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)

    visualize.plot_stats(stats, ylog=True, view=True, filename="stats/feedforward-fitness.svg")
    #visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")

    node_names = {-1: 'easy1', -2: 'easy2', -3: 'easy3', 
        -4: 'easy4', -5: 'easy5', -6: 'easy6', 
        -7: 'mod1', -8: 'mod2', -9: 'mod3', -10: 'mod4', 
        -11: 'hard1', -12: 'hard2', -13: 'hard3', 
        0: 'reroll'}
    visualize.draw_net(config, winner, True, node_names=node_names)

    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="stats/winner-feedforward.gv")
    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="stats/winner-feedforward-enabled-pruned.gv", prune_unused=True)


if __name__ == '__main__':
    run()
