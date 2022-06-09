import random
from enum import IntEnum
from numpy import roll

from src.base.game import Game, Turn
from src.zombie.zombieDicePlayers import *

class ZombieDiceType(IntEnum):
    none = 0
    brain = 1
    step = 2
    explosion = 3

class ZombieDice(object):
    def __init__(self):
        self.state = ZombieDiceType.none

    def roll(self):
        dice = ([ZombieDiceType.brain for _ in range(self.brains)] + 
            [ZombieDiceType.step for _ in range(self.steps)] + 
            [ZombieDiceType.explosion for _ in range(self.explosions)])
        random.shuffle(dice)
        result = dice[0]
        self.state = result
        return result

class ZombieDiceEasy(ZombieDice):
    def __init__(self):
        super().__init__()
        self.brains = 3
        self.steps = 2
        self.explosions = 1

class ZombieDiceModerate(ZombieDice):
    def __init__(self):
        super().__init__()
        self.brains = 2
        self.steps = 2
        self.explosions = 2

class ZombieDiceHard(ZombieDice):
    def __init__(self):
        super().__init__()
        self.brains = 1
        self.steps = 2
        self.explosions = 3                

class ZombieDiceTurn(Turn):
    def __init__(self, player, **kwargs):
        super().__init__(player)
        self.dice_to_roll = 3
        self.dice = ([ZombieDiceEasy() for _ in range(kwargs["number_dice_easy"])] + 
            [ZombieDiceModerate() for _ in range(kwargs["number_dice_moderate"])] + 
            [ZombieDiceHard() for _ in range(kwargs["number_dice_hard"])])
        self.limit_explosions = kwargs["limit_explosions"]

    def play(self, return_neural_form = True):
        """
        Rolls new dice according to specification. If all dice are said not to
        roll, the turn is over. 

        Parameter:
        array of int : rerolls
            Array of indexes for the dices to reroll. This function verifyes
            that only steps dice are rerolled
        """
        unrolled_dice = [index for index, dice in enumerate(self.dice) if dice.state == ZombieDiceType.none]
        random.shuffle(unrolled_dice)
        rolled_steps = [index for index, dice in enumerate(self.dice) if dice.state == ZombieDiceType.step]
        
        for index_step in rolled_steps:
            self.dice[index_step].roll()

        for index_dice in unrolled_dice[:self.dice_to_roll-len(rolled_steps)]:
            self.dice[index_dice].roll()    

        return (self.get_stale_state() if return_neural_form else self.dice)
        
    def get_stale_state(self):
        """
        Format what the ouput would be at this point in the game to be used by a
        neural network. Namely, the state of the game will be returned as an
        array of values, float or integer. 

        Parameter:
        array of int : rerolls
            Array of indexes for the dices to reroll. This function verifyes
            that only steps dice are rerolled
        """
        return list([int(dice.state) for dice in self.dice])

    def validate_turn(self):
        turn_validated = True

        rolled_explosions = [index for index, dice in enumerate(self.dice) if dice.state == ZombieDiceType.explosion]
        if len(rolled_explosions) >= self.limit_explosions:
            turn_validated = False
        
        return turn_validated

    def turn_ended(self):
        can_still_play = self.validate_turn()

        unrolled_dice = [index for index, dice in enumerate(self.dice) if dice.state == ZombieDiceType.none]
        all_dice_used = not bool(unrolled_dice)

        rolled_steps = [index for index, dice in enumerate(self.dice) if dice.state == ZombieDiceType.step]
        can_reroll = bool(rolled_steps)
        can_still_play = can_still_play and (not all_dice_used or (all_dice_used and can_reroll))
        return not can_still_play

    def get_points(self):
        if self.validate_turn():
            rolled_brains = [index for index, dice in enumerate(self.dice) if dice.state == ZombieDiceType.brain]
            return len(rolled_brains)
        else:
            return 0

class ZombieDiceGame(Game):
    def __init__(self, players, number_dice_easy=6, number_dice_moderate=4, 
        number_dice_hard=3, limit_explosions=3, limit_brains=13):
        super().__init__(players)
        self.turn_arguments = {"number_dice_easy":number_dice_easy,
            "number_dice_moderate":number_dice_moderate,
            "number_dice_hard":number_dice_hard,
            "limit_explosions":limit_explosions}
        self.limit_brains = limit_brains
        self.limit_turns = 25

    def play(self):
        index = 0
        while self.game_active:
            if index % len(self.players) == 0:
                self.number_turns += 1
            active_player = self.players[index]
            index = (index + 1) % len(self.players)
            turn = ZombieDiceTurn(active_player, **self.turn_arguments)
            reroll = True
            while reroll:
                inputs = turn.get_stale_state()
                reroll = active_player.play(inputs)
                if reroll:
                    turn.play()
                if turn.turn_ended():
                    reroll = False
            active_player.give_brains(turn.get_points())
            self.game_active = self.validate_game()
        winners = [player for player in self.players if player.get_brains() == max([p.get_brains() for p in self.players])]
        losers = [player for player in self.players if player.get_brains() != max([p.get_brains() for p in self.players])]
        for winner in winners:
            if len(winners) >= 2:
                winner.register_draw()
            else:
                winner.register_win()
        for loser in losers:
            loser.register_loss()
        return winners

    def validate_game(self):
        game_validated = self.number_turns < self.limit_turns
        brains = [player.get_brains() for player in self.players]
        if any([b >= self.limit_brains for b in brains]):
            if self.countdown is None:
                self.countdown = len(self.players)-1
            else:
                self.countdown -= 1
            if self.countdown == 0:
                game_validated = False
        return game_validated

    def reset(self):
        super().reset()

def progress_bar(current, total, bar_length=40):
    fraction = current / total

    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    ending = '\n' if current == total else '\r'

    print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%', end=ending)

if __name__ == "__main__":
    number_games = 100000    

    '''players1 = [GreedyZombie('Greedy'), SafeZombie('Safe'), IntelligentZombie('AI', 'stats/best_player_feedforward_1', 'config-feedforward'), IntelligentZombie('AI', 'stats/best_player_feedforward_1', 'config-feedforward'), IntelligentZombie('AI', 'stats/best_player_feedforward_1', 'config-feedforward')]
    players2 = [IntelligentZombie('AI', 'stats/best_player_feedforward_1', 'config-feedforward'), IntelligentZombie('AI', 'stats/best_player_feedforward_1', 'config-feedforward'), GreedyZombie('Greedy'), SafeZombie('Safe'), IntelligentZombie('AI', 'stats/best_player_feedforward_1', 'config-feedforward')]
    for player1, player2 in zip(players1, players2):
        players = [player1, player2]
        game = ZombieDiceGame(players)
        for _ in range(number_games):
            for player in players:
                player.reset()
            game.play()
            game.reset()
        print(f"{str(player1)}:{player1.get_winrate()}({player1.get_wins()}) ;
        {str(player2)}:{player2.get_winrate()}({player2.get_wins()})")
    '''
    for n in range(2, 11):
        print(f"{n} players:\n")
        players = [GreedyZombie(str(i)) for i in range(n)]
        game = ZombieDiceGame(players)
        for _ in range(number_games):
            for player in players:
                player.reset()
            game.play()
            game.reset()
        print('\n'.join([f"{str(player)}:{player.get_winrate()}({player.get_wins()};{player.get_draws()};{player.get_losses()})" for player in players]))