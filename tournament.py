import math

from game import Game, Turn
from random import shuffle
from enum import IntEnum

from player import Player, RandomPlayer
from zombieDicePlayers import SafeZombie, GreedyZombie, IntelligentZombie, RandomZombie
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
    def __init__(self, players, size_bracket, number_games, gameClass=Game, 
        randomPlayerClass=RandomPlayer, tiebreaker='keep_playing') -> None:

        #Players related
        self.players = players
        self.randomPlayerClass = randomPlayerClass

        #Game related
        self.size_bracket = size_bracket
        self.number_games = number_games
        self.gameClass = gameClass
        self.tiebreaker = tiebreaker

        #Tournament related
        self.contestants = []

    def preleminary_selection(self, number_prep_games=100):
        number_contestants = int(math.pow(self.size_bracket, 
            math.floor(math.log(len(self.players), self.size_bracket))))
        results = []
        for index, player in enumerate(self.players):
            players = [player] + [self.randomPlayerClass(f'random{i}') for i in range(self.size_bracket-1)]
            bracket = Bracket(players, number_prep_games, self.gameClass)
            bracket.play()
            results.append((index, player.get_wins()))
        results.sort(key=lambda d : d[1])
        results = results[:number_contestants]
        results.reverse()
        print(results)
        self.contestants = [self.players[index] for index, _ in results]
        return self.contestants

if __name__ == "__main__":
    number_games = 5000
    players = ([RandomZombie('MyRandom' + str(i), seed=i) for i in range(300)] + 
        [GreedyZombie('Greedy'), SafeZombie('Safe'), IntelligentZombie('AI', 'stats/best_player_feedforward_1', 'config-feedforward')])
    tournament = Tournament(players, 4, number_games, ZombieDiceGame, RandomZombie)
    print(tournament.preleminary_selection())
    
    '''winner = bracket.play()[0]
    print('\n'.join([f"{str(player)}:{player.get_winrate()}({player.get_wins()};{player.get_draws()};{player.get_losses()})"
        for player in players]))
    print(winner)
    print(bracket.history)'''