import random
import uuid

class Player:
    def __init__(self, name, decision_function = None):
        self.decision_function = decision_function
        self.wins = 0
        self.losses = 0
        self.draws = 0

        self.tournament_position = 0

        # Info related
        self.name = name
        self.uuid = uuid.uuid4()

    def play(self, inputs):
        return self.decision_function(inputs)

    def register_win(self):
        self.wins += 1

    def register_loss(self):
        self.losses += 1

    def register_draw(self):
        self.draws += 1

    def get_wins(self):
        return self.wins

    def get_losses(self):
        return self.losses

    def get_draws(self):
        return self.draws

    def get_winrate(self):
        return self.wins/(self.wins+self.losses)

    def get_lossrate(self):
        return self.losses/(self.wins+self.losses)

    def set_tournament_position(self, position):
        self.tournament_position = position

    def increment_tournament_position(self):
        self.tournament_position += 1

    def get_tournament_position(self):
        return self.tournament_position

    def reset(self):
        pass

    def reset_wins(self):
        self.wins = 0
        self.losses = 0
        self.draws = 0

    @staticmethod
    def find_player(uuid, players):
        for player in players:
            if player.uuid == uuid:
                return player

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self.name)

class RandomPlayer(Player):
    '''A player that plays randomly'''
    def __init__(self, name, seed=None):
        random.seed(seed)
        def decision_function(inputs):
            return random.randint(0, 1)
        super().__init__(name, decision_function)