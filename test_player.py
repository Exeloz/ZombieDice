import os
import pickle

import numpy as np
from matplotlib import pyplot as plt

import neat
import src.zombie.zombieDiceGame

# load the winner
player_filename = "best_player_1"
with open(player_filename, 'rb') as f:
    player = pickle.load(f)
    print('Loaded genome:')
    print(player)

scores = []
for _ in range(5000000):

    game = zombieDiceGame.ZombieDiceGame()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)

    net = neat.nn.FeedForwardNetwork.create(player, config)

    reroll = True
    fitness = 0.0
    #print(game.get_stale_state())
    while reroll:
        inputs = game.get_stale_state()
        action = net.activate(inputs)[0]

        # Do we reroll?
        reroll = bool(round(min(1, max(0, action))))
        if reroll: 
            game.roll()
            #print(game.get_stale_state())

        # Stop if the to many explosions occured of if all dice are used and
        # no rerolls can be achieved
        if game.turn_ended():
            reroll = False

        fitness = game.get_points()
    scores.append(fitness)
    if _%100 ==0: print(f"{_} : Score: {fitness}")

scores.sort()
plt.plot(range(len(scores)), scores)
plt.show()