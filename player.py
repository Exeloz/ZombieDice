class Player:
    def __init__(self, decision_function = None):
        self.decision_function = decision_function

    def play(self, inputs):
        return self.decision_function(inputs)

