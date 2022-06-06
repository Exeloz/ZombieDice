from game import Game, Turn
from random import shuffle
from enum import IntEnum

from zombieDicePlayers import GreedyZombie
from zombieDiceGame import ZombieDiceGame

class TieBreaker(IntEnum):
    keep_playing = 1
    check_draws = 2
    earliest_win = 3

class Bracket:
    def __init__(self, players, number_games, gameClass=Game, tiebreaker='keep_playing'):
        self.players = players
        self.gameClass = gameClass
        self.number_games = number_games
        self.tiebreaker = tiebreaker

        self.history = []

    def play(self):
        game = self.gameClass(self.players)
        for _ in range(self.number_games):
            winners = self.play_single_game(game)
            self.history.append(tuple([str(winner) for winner in winners]))
            self.shuffle_players()
        while(len(self.get_winners()) >= 2):
            self.play_single_game(game)
            self.shuffle_players()
        return self.get_winners()

    def play_single_game(self, game):
        for player in self.players:
            player.reset()
        winners = game.play()
        game.reset()
        return winners

    def shuffle_players(self):
        shuffle(self.players)

    def get_winners(self):
        winners = [player for player in self.players if player.get_wins() == max([p.get_wins() for p in self.players])]
        return winners

class Tournament:
    def __init__(self, players, size_bracket, number_games, tiebreaker='keep_playing') -> None:
        self.players = players
        self.size_bracket = size_bracket
        self.number_games = number_games
        self.tiebreaker = tiebreaker

if __name__ == "__main__":
    number_games = 1000    
    players = [GreedyZombie(str(i)) for i in range(3)]
    bracket = Bracket(players, number_games, ZombieDiceGame)
    winner = bracket.play()[0]
    print(f"{str(winner)}:{winner.get_winrate()}({winner.get_wins()};{winner.get_draws()};{winner.get_losses()})")
    print(bracket.history)