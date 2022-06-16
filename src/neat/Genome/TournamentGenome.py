from src.neat.Genome.PrunedGenome import PrunedGenome


class TournamentGenome(PrunedGenome):
    def __init__(self, key) -> None:
        super().__init__(key)
        self.last_time_winner = None

    @staticmethod
    def from_child_class(genome):
        new_genome = TournamentGenome(genome.key)
        new_genome.__dict__.update(genome.__dict__)
        return new_genome

    def get_last_time_winner(self):
        return self.last_time_winner

    def set_last_time_winner(self, gen):
        self.last_time_winner = gen