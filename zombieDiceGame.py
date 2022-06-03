import random
from enum import IntEnum

from numpy import roll

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

class ZombieDiceGame(object):
    def __init__(self, number_dice_easy=6, number_dice_moderate=4, number_dice_hard=3):
        self.game_active = True
        self.dice_to_roll = 3
        self.dice = ([ZombieDiceEasy() for _ in range(number_dice_easy)] + 
            [ZombieDiceModerate() for _ in range(number_dice_moderate)] + 
            [ZombieDiceHard() for _ in range(number_dice_hard)])
        self.limit_explosions = 3

    def roll(self, return_neural_form = True):
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

if __name__ == "__main__":
    easy = ZombieDiceEasy()
    print("easy:")
    for _ in range(5):
       print(easy.roll())

    moderate = ZombieDiceModerate()
    print("moderate:")
    for _ in range(5):
        print(moderate.roll())

    hard = ZombieDiceHard()
    print("hard:")
    for _ in range(5):
        print(hard.roll())

    game = ZombieDiceGame()
    print("game:")
    for _ in range(5):
        print(game.roll())
        print(f"{game.get_points()} points")