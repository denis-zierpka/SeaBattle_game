#
# Created by Denis Zierpka on 13.02.2021
#

import curses
from curses import wrapper
import random
import argparse
import pickle
import os
from SeaBattle import SeaBattle
from SeaBattle import Player


DEBUG = False
PATH_TO_CACHE = 'seabattle/data.pickle'
PADDING_TOP = 3


def get_player_name():
    input_message = 'Please enter your name:  '
    name = input(input_message)
    while len(name) > 15:
        name = input('Please enter a name with 15 or less characters:  ')
    return name


def load_to_data(game):
    data = dict()
    data["opponents_field"] = game.opponents_field
    data["opponents_real_field"] = game.opponents_real_field
    data["opponents_ships"] = game.opponents_ships
    data["our_field"] = game.our_field
    data["our_ships"] = game.our_ships
    data["height"] = game.height
    data["width"] = game.width
    data["name1"] = game.player_name_1
    data["name2"] = game.player_name_2
    return data


def load_from_data(game):
    with open(PATH_TO_CACHE, 'rb') as f:
        data = pickle.load(f)

        game.opponents_field = data["opponents_field"]
        game.opponents_real_field = data["opponents_real_field"]
        game.opponents_ships = data["opponents_ships"]
        game.our_field = data["our_field"]
        game.our_ships = data["our_ships"]
        game.height = data["height"]
        game.width = data["width"]
        game.player_name_1 = data["name1"]
        game.player_name_2 = data["name2"]


def show_winning_info(screen, game):
    try:
        screen.clear()
        screen.addstr(2, 0, ("You" if game.who_wins() == Player.USER else "Computer") \
                      + ' won!' + "\n" + "Press any key to exit.")
        with open(PATH_TO_CACHE, 'wb') as f:
            pickle.dump({}, f)

        screen.getch()
        return
    except KeyboardInterrupt:
        return


def play(game, screen, was_data_loaded):
    screen.clear()

    row_input = ''
    column_input = ''
    where_to_enter = 0
    wrong_input = 0
    show_info_about_exit = 0
    
    if not was_data_loaded:
        game.generate_fields(game.opponents_real_field, Player.ENEMY)
        game.generate_fields(game.our_field, Player.USER)
    player_has_accepted_the_field = False

    while True:
        if DEBUG:
            game.opponents_field = game.opponents_real_field

        screen.clear()
        screen_height, screen_width = screen.getmaxyx()

        required_height = 2 * (game.width * 2 + 1) + 18
        if screen_width < required_height:
            return 'window'

        screen.addstr(0, 0, game.fields_str(screen_width))

        if show_info_about_exit:
            screen.addstr(game.height + PADDING_TOP, 0, "Press f to exit!")
            show_info_about_exit = 0

        if not player_has_accepted_the_field:
            screen.addstr(game.height + PADDING_TOP + 1, 0, "Do you want to play with this field? y/n")
            start = screen.getch()
            if start == ord('n'):
                game.generate_fields(game.our_field, Player.USER)
                game.generate_fields(game.opponents_real_field, Player.ENEMY)
                continue
            elif start == ord('y'):
                screen.addstr(game.height + PADDING_TOP + 1, 0, '')
                player_has_accepted_the_field = True
            elif start == ord('f'):
                return
            else:
                show_info_about_exit = 1

        if player_has_accepted_the_field:
            if wrong_input:
                screen.addstr(game.height + PADDING_TOP + 1, 0, "Check the entered coordinates!")
                wrong_input = 0

            screen.addstr(game.height + PADDING_TOP + 2, 0, "Line (from top to bottom): " + row_input, curses.A_REVERSE)
            if where_to_enter == 1:
                screen.addstr(game.height + PADDING_TOP + 3, 0, "Column (from left to right): " + column_input, curses.A_REVERSE)

            c = screen.getch()
            if c == ord('f'):
                return
            elif c == ord('\n'):
                where_to_enter += 1
                if where_to_enter == 2:
                    try:
                        game.shoot_field(game.opponents_field, Player.ENEMY, int(row_input), int(column_input))
                        if game.who_wins() != 0:
                            show_winning_info(screen, game)
                            return
                    except Exception:
                        wrong_input = 1

                    if not wrong_input:
                        while True:
                            try:
                                game.shoot_field(game.our_field, Player.USER, random.randint(1, game.height), random.randint(1, game.width))
                                break
                            except Exception:
                                continue

                    if game.who_wins() != 0:
                        show_winning_info(screen, game)
                        return

                    with open(PATH_TO_CACHE, 'wb') as f:
                        pickle.dump(load_to_data(game), f)

                    row_input = ''
                    column_input = ''
                    where_to_enter = 0
            elif chr(c) == '\x7f':
                if where_to_enter == 0:
                    row_input = row_input[:-1]
                elif where_to_enter == 1:
                    column_input = column_input[:-1]
            elif 48 <= c <= 57:
                if where_to_enter == 0:
                    row_input += chr(c)
                elif where_to_enter == 1:
                    column_input += chr(c)
            else:
                show_info_about_exit = True


def main(screen, player_name_1, player_name_2, field_height, field_width, was_data_loaded):
    game = SeaBattle(player_name_1, player_name_2, field_height, field_width)

    if was_data_loaded:
        load_from_data(game)

    screen.clear()
    screen_size = ''

    while True:
        welcome_str = '####################################\n' \
                    + '##      WELCOME TO SEABATTLE      ##\n' \
                    + '####################################\n\n'

        player_names_str = 'Your name: {}\n'.format(player_name_1)
        instructions_str = '\n\nPress s to start the game.\nPress f to exit.'

        screen.clear()
        screen.addstr(0, 0, welcome_str + player_names_str + instructions_str + screen_size)

        c = screen.getch()

        if c == ord('f'):
            return
        elif c == ord('s'):
            screen_size = ''
            if play(game, screen, was_data_loaded) == 'window':
                screen_size = '\n\nProgram window is not big enough'


def ask_about_the_last_game():
    with open(PATH_TO_CACHE, 'rb') as f:
        data = pickle.load(f)
        if len(data) != 0:
            print("Do you want to continue the last game?")
            ans = input("Answer(y/n): ")
            if ans == 'n':
                data = {}
                with open(PATH_TO_CACHE, 'wb') as f:
                    pickle.dump(data, f)
                return 0
            elif ans == 'y':
                return 1
            else:
                return 2
        return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("height", help="needs height of the field", type=int)
    parser.add_argument("width", help="needs width of the field", type=int)
    args = parser.parse_args()

    print("Playing Sea Battle")
    print()

    local_was_data_loaded = 0
    try:
        local_was_data_loaded = ask_about_the_last_game()
        while local_was_data_loaded == 2:
            local_was_data_loaded = ask_about_the_last_game()
    except EnvironmentError:
        print("Could not find cache, new game will be start")
        local_was_data_loaded = 0

    local_player_name_1 = 'Player 1'
    local_player_name_2 = 'Player 2'
    local_field_height = args.height
    local_field_width = args.width

    if not local_was_data_loaded:
        local_player_name_1 = get_player_name() or 'Player 1'
        local_player_name_2 = 'Player 2'

    wrapper(main, local_player_name_1, local_player_name_2, local_field_height, local_field_width, local_was_data_loaded)




