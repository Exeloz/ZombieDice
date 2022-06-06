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
    def __init__(self, players, number_games, gameClass=Game, tiebreaker=TieBreaker.keep_playing):
        self.players = players
        self.gameClass = gameClass
        self.number_games = number_games
        self.tiebreaker = tiebreaker

        self.history = []

    def play(self):
        self.game = self.gameClass(self.players)
        for _ in range(self.number_games):
            winners = self.play_single_game(self.game)
            self.__register_game__(winners)
            self.shuffle_players()
        return self.get_winners()

    def play_single_game(self, game):
        for player in self.players:
            player.reset()
        winners = game.play()
        game.reset()
        return winners

    def break_tie(self, players):
        if self.tiebreaker == TieBreaker.keep_playing:
            return self.__tiebreaker_keep_playing__()
        elif self.tiebreaker == TieBreaker.check_draws:
            return self.__tiebreaker_check_draws__(players)
        elif self.tiebreaker == TieBreaker.earliest_win:
            return self.__tiebreaker_earliest_win__(players)
        else:
            raise NotImplemented

    def shuffle_players(self):
        shuffle(self.players)

    def get_winners(self):
        winners = [player for player in self.players if player.get_wins() == max([p.get_wins() for p in self.players])]
        while len(winners) >= 2:
            winners = self.break_tie(winners)
        return winners

    def __tiebreaker_keep_playing__(self):
        winners = self.play_single_game(self.game)
        self.__register_game__(winners)
        self.shuffle_players()
        return self.get_winners()

    def __tiebreaker_check_draws__(self, players):
        draws = [(player, player.get_draws()) for player in players]
        winner = max(draws, key=lambda d : d[1])[0]
        return [winner]

    def __tiebreaker_earliest_win__(self, players):
        for past_winner in self.history:
            for player in players:
                if len(past_winner) == 1 and past_winner[0] == str(player):
                    return [player]

    def __register_game__(self, winners):
        self.history.append(tuple([str(winner) for winner in winners]))

class Tournament:
    def __init__(self, players, size_bracket, number_games, tiebreaker='keep_playing') -> None:
        self.players = players
        self.size_bracket = size_bracket
        self.number_games = number_games
        self.tiebreaker = tiebreaker

if __name__ == "__main__":
    number_games = 5000
    players = [GreedyZombie(str(i)) for i in range(3)]
    bracket = Bracket(players, number_games, ZombieDiceGame)
    winner = bracket.play()[0]
    print('\n'.join([f"{str(player)}:{player.get_winrate()}({player.get_wins()};{player.get_draws()};{player.get_losses()})"
        for player in players]))
    print(winner)
    print(bracket.history)