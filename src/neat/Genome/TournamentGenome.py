from src.neat.Genome.PrunedGenome import PrunedGenome


class TournamentGenome(PrunedGenome):
    def __init__(self, key) -> None:
        super().__init__(key)
        self.last_time_winner = None

    def get_last_time_winner(self):
        return self.last_time_winner

    def set_last_time_winner(self, gen):
        self.last_time_winner = gen