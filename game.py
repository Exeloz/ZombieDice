class Turn(object):
    def __init__(self, player):
        self.player = player

    def play(self, return_neural_form = True):
        """
        Play a step in a turn.
        """
        raise NotImplemented
        
    def get_stale_state(self):
        """
        Format what the ouput would be at this point in the game to be used by a
        neural network. Namely, the state of the game will be returned as an
        array of values, float or integer. 
        """
        raise NotImplemented

    def validate_turn(self):
        raise NotImplemented


    def turn_ended(self):
        """
        Verify if all steps led to the turn ending. 
        """
        raise NotImplemented

    def get_points(self):
        raise NotImplemented


class Game(object):
    def __init__(self, players):
        self.players = players

        #Relative to current game
        self.game_active = True
        self.number_turns = 0
        self.countdown = None

    def play(self):
        """
        Plays a game. Most likely, turns will have to be created. 
        """
        raise NotImplemented

    def validate_game(self):
        raise NotImplemented

    def reset(self):
        self.game_active = True
        self.number_turns = 0
        self.countdown = None

