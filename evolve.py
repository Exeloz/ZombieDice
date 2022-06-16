import math
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import ray

import neat
import src.neat.visualize as visualize
from src.base.tournament import Tournament
from src.neat.Genome.TournamentGenome import TournamentGenome
from src.neat.Reproduction.TournamentReproduction import TournamentReproduction
from src.neat.Stagnation.TournamentStagnation import TournamentStagnation
from src.zombie.zombieDiceGame import ZombieDiceGame
from src.zombie.zombieDicePlayers import (GreedyZombie, RandomZombie,
                                          StudentZombie)


class ZombieEvolver:
    def __init__(self, config_filename, n_gens = 1000, n_against = 4, n_cpus = 4):
        # Config related
        self.config_filename = config_filename
        
        # Parameters related
        self.number_games = 500
        self.number_gens = n_gens
        self.n_against = n_against

        # Stat related
        self.stats_location = 'stats'
        self.genome_locations = 'checkpoints'
        self.current_gen = 0

        # Multithread related 
        self.n_cpus = n_cpus

    def eval_genome(self, zombie, previous_winner):
        if previous_winner is None:
            previous_winner_fitness = 0
        else:
            previous_winner_fitness = previous_winner.get_tournament_position()
        fitness = max(0, zombie.get_tournament_position() - previous_winner_fitness)
        if previous_winner is not None and zombie.name == previous_winner.name:
            fitness = 0.5
        return fitness

    def eval_genomes(self, genomes, config):
        previous_best_id = self.find_best_genome(genomes)
        zombies = [StudentZombie(self.create_zombie_name(genome_id), genome, config) 
                        for genome_id, genome in genomes]
        tournament = Tournament(zombies, self.n_against, self.number_games, 
            gameClass=ZombieDiceGame, randomPlayerClass=RandomZombie)
        tournament.preleminary_selection()
        winners = tournament.play()

        if previous_best_id is None:
            previous_winner = None
        else:
            previous_winner = self.find_zombie(zombies, previous_best_id)
        
        for zombie in zombies:
            zombie.genome.fitness = self.eval_genome(zombie, previous_winner)

        self.checkpoint(genomes)
        return winners

    def create_zombie_name(self, genome_id):
        return f'Student-{genome_id}'

    def find_zombie(self, zombies, genome_id):
        for zombie in zombies:
            if str(zombie) == self.create_zombie_name(genome_id):
                return zombie 

    def find_best_genome(self, genomes):
        genomes_light = [(g_id, g.fitness) for g_id, g in genomes if g.fitness is not None]
        if len(genomes_light) == 0:
            return None
        max_id = max(genomes_light, key=lambda g: g[1])[0]
        for genome_id, _ in genomes:
            if genome_id == max_id:
                return genome_id

    def checkpoint(self, genomes):
        directory_path = Path(f"{self.genome_locations}/gen{self.current_gen}")
        for genome_id, genome in genomes:
            path = Path.joinpath(directory_path, str(genome_id))
            directory_path.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as f:
                pickle.dump(genome, f)
        self.current_gen += 1

    def run(self, restore_from=None):
        ray.init(num_cpus=self.n_cpus)

        # Load the config file, which is assumed to live in
        # the same directory as this script.
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, self.config_filename)
        config = neat.Config(TournamentGenome, TournamentReproduction,
                            neat.DefaultSpeciesSet, TournamentStagnation,
                            config_path)

        # Create the population, which is the top-level object for a NEAT run.
        if restore_from is None:
            p = neat.Population(config)
        else:
            p = neat.checkpoint.Checkpointer.restore_checkpoint(restore_from)
            stagnation = config.stagnation_type(config.stagnation_config, p.reporters)
            p.reproduction = config.reproduction_type(config.reproduction_config,
                                                     p.reporters,
                                                     stagnation)
            p.config = config
            print("Restoring from {!s}".format(restore_from))

        # Add a stdout reporter to show progress in the terminal.
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1, filename_prefix=Path(f"{self.genome_locations}/neat/neat-checkpoint")))
        winner = p.run(self.eval_genomes, self.number_gens)

        # Save the winner.
        with open(f"{self.stats_location}/winner-feedforward", 'wb') as f:
            pickle.dump(winner, f)

        print(winner)

        visualize.plot_stats(stats, ylog=True, view=True, filename=f"{self.stats_location}/feedforward-fitness.svg")
        #visualize.plot_species(stats, view=True, filename=f"{stats_location}/feedforward-speciation.svg")

        inputs_nodes = {-1: 'easy1', -2: 'easy2', -3: 'easy3', 
            -4: 'easy4', -5: 'easy5', -6: 'easy6', 
            -7: 'mod1', -8: 'mod2', -9: 'mod3', -10: 'mod4', 
            -11: 'hard1', -12: 'hard2', -13: 'hard3'}
        player_nodes = dict([(-14-i, f"player{i}") for i in range(self.n_against)])
        self_nodes = {min(player_nodes.keys())-1: 'Self'}
        output_nodes = {0: 'reroll'}
        nodes_names = {}
        nodes_names.update(inputs_nodes)
        nodes_names.update(player_nodes)
        nodes_names.update(self_nodes)
        nodes_names.update(output_nodes)
        visualize.draw_net(config, winner, True, node_names=nodes_names)

        visualize.draw_net(config, winner, view=True, node_names=nodes_names,
                        filename=f"{self.stats_location}/winner-feedforward.gv")
        visualize.draw_net(config, winner, view=True, node_names=nodes_names,
                        filename=f"{self.stats_location}/winner-feedforward-enabled-pruned.gv", prune_unused=True)
        
        ray.shutdown()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        num_cpus = int(sys.argv[1])
    else:
        num_cpus = 4
    n_players = 4
    config_filename = f'configs/config-{n_players}-players'
    evolve = ZombieEvolver(config_filename, n_gens=10000, n_against=n_players, n_cpus=num_cpus)

    restore_from = 'checkpoints/neat/neat-checkpoint999'
    _ = evolve.run(restore_from)

    
