#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yatzy game by Christofer Tibbelin
from dataclasses import dataclass
from typing import List, Dict
from random import randint
import os
import time

max_players = 5
number_of_players = 0
players = []
max_retrows = 2


@dataclass
class ScoreTypes:
    ''' a score Type '''
    name: str
    ok_answers: list[str]
    function_name: str
    count_value: int
    # Should this score count towards a bonus and if so which?
    bonus: int = 0


# Special used in code to find bonus spot.
name_for_sixes = 'Sixes  (6)'

SCORE_SHEET = {
    'Aces   (1)': ScoreTypes('Aces   (1)', ['1', 'ace', 'aces', 'one', 'ones'], 'simple_score_count', 1, 1),
    'Twos   (2)': ScoreTypes('Twos   (2)', ['2', 'two', 'twos', 'dues'], 'simple_score_count', 2, 1),
    'Threes (3)': ScoreTypes('Threes (3)', ['3', 'three', 'threes'], 'simple_score_count', 3, 1),
    'Fours  (4)': ScoreTypes('Fours  (4)', ['4', 'four', 'fours'], 'simple_score_count', 4, 1),
    'Fives  (5)': ScoreTypes('Fives  (5)', ['5', 'five', 'fives'], 'simple_score_count', 5, 1),
    name_for_sixes: ScoreTypes(name_for_sixes, ['6', 'six', 'sixes'], 'simple_score_count', 6, 1),
    'One Pair': ScoreTypes('One Pair', ['pair', 'one pair', 'pairs', '11', '22', '33', '44', '55', '66'], 'count_pair_score', -1),
    'Two Pairs': ScoreTypes('Two Pairs', ['two pair', 'two pairs', '2 pair', '2 pairs'], 'count_two_pairs_score', -1),
    '3 of a kind': ScoreTypes('3 of a kind', ['3 of a kind', 'three of a kind', 'three of same', 'three of the same', '3 of same', '3 same', 'three same'], 'count_x_of_same_kind_score', 3),
    '4 of a kind': ScoreTypes('4 of a kind', ['4 of a kind', 'four of a kind', 'four of same', 'four of the same', '4 same', 'four same', '4 of same'], 'count_x_of_same_kind_score', 4),
    'Small Straight': ScoreTypes('Small Straight', ['small straight', 'small', '12345'], 'count_straight_score', 0),
    'Large Straight': ScoreTypes('Large Straight', ['large straight', 'large', '23456'], 'count_straight_score', 1),
    'Full House': ScoreTypes('Full House', ['full house', 'full', 'house'], 'count_full_house_score', 1),
    'Chance': ScoreTypes('Chance', ['chance', 'any'], 'count_chance_score', 0),
    'YATZY': ScoreTypes('YATZY', ['yatzy', 'yatzee', 'yatze'], 'count_yatzy_score', 5)
}


@dataclass
class Score:
    ''' a single score '''

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return self.name


@dataclass
class Player:
    ''' a Yatzy Player '''

    def __init__(self, name: str):
        self.name = name
        self.scores: Dict[str, Score] = {}
        self.total_score: int = 0
        self.first_bonus: int = 0
        self.top_total: int = 0

    def __repr__(self) -> str:
        return self.name


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def normalize(string: str) -> str:
    string = string.replace(' ', '')
    string = string.replace('-', '')
    string = string.replace('_', '')
    return string.lower()


def convert_to_list(string):
    string2 = string.replace(" ", "")
    return [int(a) for a in str(string2)]


def roll_one_dice():
    return randint(1, 6)


def roll_dices(amount):
    rolled_dices = []
    for x in range(amount):
        rolled_dices.append(roll_one_dice())
    return rolled_dices


def get_amount_of_players():
    answer = 0
    while answer < 1 or answer > max_players:
        try:
            answer = int(
                input(f"How many players want to play? 1-{max_players}? "))
        except ValueError:
            print("This was not a valid input please try again")
    return answer


def ordinal_short(number: int):
    if number == 1:
        return "1st"
    elif number == 2:
        return "2nd"
    elif number == 3:
        return "3rd"
    else:
        return f"{number}th"


def ordinal_long(number: int):
    if number == 1:
        return "first"
    elif number == 2:
        return "second"
    elif number == 3:
        return "third"
    elif number == 3:
        return "fourth"
    else:
        return f"{number}th"


def init_players(number_of_players: int):
    _players = []
    for x in range(number_of_players):
        s = input(f"Enter name of {ordinal_short(x+1)} player: ")
        _player_name = ''.join([s[0].upper(), s[1:]])
        _players.append(Player(_player_name))
    return _players


def welcome_players(players: List[Player]):
    print("Welcome!!", end=' ')
    pos = -1
    for player in players:
        pos += 1
        if pos == len(players) - 1:
            print("and", player.name)
        else:
            print(player.name, end=', ')


def print_player_scores_left(player: Player):
    print('------------------------------------')
    print("availible types left:")
    for i, score_key in enumerate(SCORE_SHEET):
        if score_key in player.scores:
            pass
        else:
            if i % 3 == 0:
                print("")
            print(f"{'|': <4}", end='')
            print(f"{score_key: <16}", end='')
            print(f"{'': <2}", end='')
    print("")
    print('------------------------------------')


def get_dices_to_reroll():
    while(True):
        try:
            dice_to_reroll = convert_to_list(
                input("Which dices do you wish to roll again? "))
        except ValueError:
            print("This was not a valid input please try again")
            continue
        if len(dice_to_reroll) == 1 and dice_to_reroll[0] == 0:
            cls()
            print("Great that you are happy already!!")
            return []
        if len(dice_to_reroll) > 5:
            print("Sorry you can't reroll more dices than you have...")
            continue
        found_error = False
        for dice in dice_to_reroll:
            if dice < 1 or dice > 5:
                found_error = True
        if found_error:
            print("Sorry wrong answer should be like between 1-5 and like 2 3 5")
        else:
            return dice_to_reroll


def simple_score_count(dices: List[int], dice_to_count: int):
    score_value = 0
    for dice in dices:
        if dice_to_count == dice:
            score_value += dice
    return score_value


def count_pair_score(dices: List[int], notused):
    dices.sort(reverse=True)
    for i, dice in enumerate(dices):
        if i > len(dices)-2:
            return 0
        if dice == dices[i+1]:
            return dice * 2
    return 0


def count_two_pairs_score(dices: List[int], notused):
    dices.sort(reverse=True)
    temp_score = 0
    prev_dice = 0
    for i, dice in enumerate(dices):
        if i > len(dices)-2:
            return 0
        if dice == prev_dice:
            continue
        if dice == dices[i+1]:
            if temp_score != 0:
                return temp_score + (dice * 2)
            temp_score = dice * 2
        prev_dice = dice
    return 0


def count_x_of_same_kind_score(dices: List[int], how_many: int):
    dices.sort(reverse=True)
    temp_score = 0
    found = 0
    for i, dice in enumerate(dices):
        if i > len(dices)-how_many:
            return 0
        for x in range(how_many):
            if dice == dices[i+x]:
                temp_score += dice
                found += 1
            else:
                temp_score = 0
                found = 0
                break
        if found == how_many:
            return temp_score
    return 0


def count_straight_score(dices: List[int], is_large: int):
    dices.sort(reverse=False)
    if is_large == 1:
        prev_dice = 1
    else:
        prev_dice = 0
    found = 0
    for dice in dices:
        if dice == prev_dice + 1:
            found += 1
            prev_dice = dice
        else:
            return 0
    if is_large == 1:
        return 20
    else:
        return 15


def count_full_house_score(dices: List[int], not_used):
    dices.sort(reverse=False)
    temp_score = 0
    last_dice = 0
    for x in range(2):
        prev_dice = dices[0]
        temp_list = []
        for i in range(3):
            dice = dices.pop(0)
            if last_dice == dice:
                return 0
            if dice == prev_dice:
                prev_dice = dice
                temp_list.append(dice)
                temp_score += dice
                if len(dices) == 0:
                    return temp_score
            elif len(temp_list) == 2 or len(temp_list) == 3:
                dices.append(dice)
                last_dice = prev_dice
                break
            else:
                return 0
        last_dice = prev_dice
    return 0


def count_yatzy_score(dices: List[int], not_used):
    prev_dice = dices[0]
    for dice in dices:
        if dice != prev_dice:
            return 0
    return 50


def count_chance_score(dices: List[int], not_used):
    score = 0
    for dice in dices:
        score += dice
    return score


def get_player_score(dices: List[int], player: Player) -> Dict[str, Score]:
    while True:
        keep_score_on = input(
            "Which score do you want to put your dices on? ")
        for score_key in SCORE_SHEET:
            curr_score = SCORE_SHEET[score_key]
            for ok_answer in curr_score.ok_answers:
                if normalize(keep_score_on) == normalize(ok_answer):
                    if curr_score.name in player.scores:
                        print('You already have that score!')
                        break
                    else:
                        score_value: int = globals()[curr_score.function_name](
                            dices, curr_score.count_value)
                        print(f"{player.name} you got {score_value} points")
                        # Return dictionary with key and Score as value
                        return {curr_score.name: Score(curr_score.name, score_value)}
        print('That was not a correct answer, try again...')


def fake_score(players: List[Player]):
    for key in SCORE_SHEET:
        for player in players:
            player.scores[key] = Score(key, randint(0, 20))


def calculate_total_score(players: List[Player]):
    for player in players:
        tempbonus = 0
        for key1, score1 in player.scores.items():
            player.total_score += score1.value
        for key2, score2 in SCORE_SHEET.items():
            if score2.bonus == 1:
                tempbonus += player.scores[key2].value
        player.top_total = tempbonus
        if tempbonus > 63:
            player.first_bonus = 50
            player.total_score += 50


def print_end_score(players: List[Player]):
    width = (len(players)*20)+10
    print("")
    print("")
    print("Total score is:")

    print(f"{'Score:': <20}", end='')
    for player in players:
        print(f"{player.name : <20}", end='')
    print("")
    print(f"{'':-<{width}}")
    for key, score in SCORE_SHEET.items():
        scorename = key + ':'
        print(f"{scorename: <20}", end='')
        for player in players:
            print(f"{player.scores[key].value: <20}", end='')
        print("")
        if key == name_for_sixes:
            print(f"{'':-<{width}}")
            print(f"{'Top Total:': <20}", end='')
            for player in players:
                print(f"{player.top_total: <20}", end='')
            print("")
            print(f"{'Top Bonus:': <20}", end='')
            for player in players:
                print(f"{player.first_bonus: <20}", end='')
            print("")
            print(f"{'':-<{width}}")

    print(f"{'':-<{width}}")
    print(f"{'Grand Total:': <20}", end='')
    for player in players:
        print(f"{player.total_score: <20}", end='')
    print("")
    print(f"{'':-<{width}}")


def print_current_dice_roll(name: str, retry: int, dices: List[int]):
    print(f"{name}, here is your {ordinal_long(retry+1)} throw.")
    print(dices)
    print(" ^  ^  ^  ^  ^")
    print(" 1  2  3  4  5 or 0")


def main():
    print("Welcome to Yahtzee!")
    print('----------------------')
    number_of_players = get_amount_of_players()
    players: List[Player] = init_players(number_of_players)
    cls()
    welcome_players(players)
    # To fake Score and show quick:
    # fake_score(players)
    # calculate_total_score(players)
    # print_end_score(players)
    for round in range(len(SCORE_SHEET)):
        for player in players:
            dices = []
            print(f"{player.name}'s turn!")
            dices = roll_dices(5)
            for retry in range(max_retrows):
                print_player_scores_left(player)
                print_current_dice_roll(player.name, retry, dices)
                dice_to_reroll = get_dices_to_reroll()
                if len(dice_to_reroll) == 0:
                    break
                for dice_num in dice_to_reroll:
                    dices[dice_num-1] = roll_one_dice()
                cls()
            print_player_scores_left(player)
            print(f"{player.name}, here are your dices.")
            print(dices)
            player.scores.update(get_player_score(dices, player))
            time.sleep(2.0)
            cls()
    calculate_total_score(players)
    print_end_score(players)


if __name__ == "__main__":
    main()
