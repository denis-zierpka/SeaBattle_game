#
# Created by Denis Zierpka on 13.02.2021
#

import random
from enum import Enum
from ship import Ship


EMPTY_CELL = 'O'
ALIVE_SHIP_CELL = '*'
MISS_SHIP_CELL = '-'
SHOOT_SHIP_CELL = 'X'
DESTROYED_SHIP_CELL = 'F'


class Player(Enum):
    USER = 1
    ENEMY = 2


class SeaBattle:
    def __init__(self, player_name_1, player_name_2, height, width):
        self.player_name_1 = player_name_1
        self.player_name_2 = player_name_2
        self.height = height
        self.width = width
        self.our_field = [[EMPTY_CELL] * width for i in range(height)]
        self.opponents_field = [[EMPTY_CELL] * width for i in range(height)]
        self.opponents_real_field = [[EMPTY_CELL] * width for i in range(height)]
        self.our_ships = []
        self.opponents_ships = []
        self.last_row = -1
        self.last_col = -1

    def fields_str(self, screen_width):
        st = '\n'
        padding_sm = (screen_width - 2 * (self.width * 2 + 1)) // 3
        padding_bi = (screen_width - 2 * (self.width * 2 + 1) - padding_sm * 2) + 3

        if self.width < 10:
            st += ' ' * padding_sm
            for j in range(self.width):
                st += str(j + 1)
                st += ' '
            st += ' ' * padding_bi
            for j in range(self.width):
                st += str(j + 1)
                st += ' '
            st += '\n'
            st += '\n'
        for i in range(self.height):
            st += ' ' * (padding_sm - len(str(i + 1)) - 3)
            st += str(i + 1)
            st += ' ' * 3
            for j in range(self.width):
                st += str(self.our_field[i][j])
                st += ' '
            st += ' ' * (padding_bi - len(str(i + 1)) - 3)
            st += str(i + 1)
            st += ' ' * 3
            for j in range(self.width):
                st += str(self.opponents_field[i][j])
                st += ' '
            if i == self.last_row:
                st += '<'
            st += '\n'
        if self.last_col != -1:
            st += ' ' * (padding_sm + 2 * self.width + padding_bi)
            st += ' ' * self.last_col * 2
            st += '^'
        st += '\n'
        return st

    def this_shot_does_not_destroy_ship(self, player, x, y):
        if player == Player.USER:
            for i in self.our_ships:
                if i.has_one_more_cell(x, y):
                    return True
            return False
        else:
            for i in self.opponents_ships:
                if i.has_one_more_cell(x, y):
                    return True
            return False

    def count_undestroyed_ships(self, player):
        cnt = 0
        for i in (self.our_ships if player == Player.USER else self.opponents_ships):
            if i.size > 0:
                cnt += 1
        return cnt

    def who_wins(self):
        if self.count_undestroyed_ships(Player.USER) == 0:
            return Player.ENEMY
        elif self.count_undestroyed_ships(Player.ENEMY) == 0:
            return Player.USER
        else:
            return 0

    def shoot_field(self, field, player, x, y):
        x -= 1
        y -= 1
        if not (0 <= x < len(field) and 0 <= y < len(field[0])):
            raise Exception('Not in the right range.')
        if field[x][y] != EMPTY_CELL and field[x][y] != ALIVE_SHIP_CELL:
            raise Exception('Field has already been shoot.')

        if player == Player.USER:
            if field[x][y] == EMPTY_CELL:
                field[x][y] = MISS_SHIP_CELL
            elif self.this_shot_does_not_destroy_ship(player, x, y):
                field[x][y] = SHOOT_SHIP_CELL
            else:
                field[x][y] = DESTROYED_SHIP_CELL
        else:
            if self.opponents_real_field[x][y] == EMPTY_CELL:
                self.opponents_field[x][y] = MISS_SHIP_CELL
                self.opponents_real_field[x][y] = MISS_SHIP_CELL
            elif self.this_shot_does_not_destroy_ship(player, x, y):
                self.opponents_field[x][y] = SHOOT_SHIP_CELL
                self.opponents_real_field[x][y] = SHOOT_SHIP_CELL
            else:
                self.opponents_field[x][y] = DESTROYED_SHIP_CELL
                self.opponents_real_field[x][y] = DESTROYED_SHIP_CELL

        if player == Player.USER:
            for i in self.our_ships:
                i.delete_cell_from_ship(x, y)
        else:
            for i in self.opponents_ships:
                i.delete_cell_from_ship(x, y)

        if player == Player.ENEMY:
            self.last_col = y
            self.last_row = x

        return 0

    def is_it_possible_to_set_a_ship(self, field, x, y, direction, size):
        if direction == 0:
            if y + size >= len(field[0]):
                return False
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + size + 1):
                    if 0 <= i < len(field) and 0 <= j < len(field[0]):
                        if field[i][j] != EMPTY_CELL:
                            return False
        else:
            if x + size >= len(field):
                return False
            for i in range(x - 1, x + size + 1):
                for j in range(y - 1, y + 2):
                    if 0 <= i < len(field) and 0 <= j < len(field[0]):
                        if field[i][j] != EMPTY_CELL:
                            return False
        return True

    def set_ship_on_field(self, field, x, y, direction, size):
        if direction == 0:
            for i in range(y, y + size):
                field[x][i] = ALIVE_SHIP_CELL
        else:
            for i in range(x, x + size):
                field[i][y] = ALIVE_SHIP_CELL

    def generate_fields(self, field, players):
        if players == Player.USER:
            self.our_ships = []
        else:
            self.opponents_ships = []

        space = self.width * self.height
        space = int(space // 5)

        for i in range(1, space):
            sum = 0
            for j in range(1, i + 1):
                sum += j * (i + 1 - j)
            if (sum > space):
                space = i - 1
                break

        while True:
            start_new = 0
            for i in range(len(field)):
                for j in range(len(field[0])):
                    if players == Player.USER:
                        field[i][j] = EMPTY_CELL
                    else:
                        self.opponents_field[i][j] = EMPTY_CELL
                        self.opponents_real_field[i][j] = EMPTY_CELL

            if players == Player.USER:
                self.our_ships = []
            else:
                self.opponents_ships = []

            for length in range(1, space + 1):
                for number in range(1, space + 1 - length + 1):
                    cnt = 0
                    while True:
                        cnt += 1
                        x_r = random.randint(0, self.height - 1)
                        y_r = random.randint(0, self.width - 1)
                        dir_r = random.randint(0, 1)
                        if self.is_it_possible_to_set_a_ship(field, x_r, y_r, dir_r, length):
                            self.set_ship_on_field(field, x_r, y_r, dir_r, length)
                            if players == Player.USER:
                                self.our_ships.append(Ship(x_r, y_r, dir_r, length, number))
                            else:
                                self.opponents_ships.append(Ship(x_r, y_r, dir_r, length, number))
                            break
                        if cnt > self.height * self.width:
                            start_new = 1
                            break

            if start_new == 0:
                break
