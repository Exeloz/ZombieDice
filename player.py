class Player:
    def __init__(self, name, decision_function = None):
        self.decision_function = decision_function
        self.name = name
        self.wins = 0
        self.losses = 0
        self.draws = 0

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

    def reset(self):
        pass

    def reset_wins(self):
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def __str__(self) -> str:
        return str(self.name)