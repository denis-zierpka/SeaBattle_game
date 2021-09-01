#
# Created by Denis Zierpka on 13.02.2021
#


class Ship:
    def __init__(self, x, y, direction, size, number):
        self.size = size
        self.number = number
        self.base = []
        if direction == 0:
            for i in range(y, y + size):
                self.base.append((x, i))

        else:
            for i in range(x, x + size):
                self.base.append((i, y))

    def delete_cell_from_ship(self, x, y):
        for i in range(len(self.base)):
            if self.base[i][0] == x and self.base[i][1] == y:
                self.base[i] = (-1, -1)
                self.size -= 1

    def has_one_more_cell(self, x, y):
        if (x, y) in self.base:
            return self.size >= 2
        return False
