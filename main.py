from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "You're trying to shoot out the board"


class BoardUsedException(BoardException):
    def __str__(self):
        return "You already shot that dot"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, nose_point, length, nose_direction):
        self.length = length
        self.nose_point = nose_point
        self.nose_direction = nose_direction
        self.durability = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.nose_point.x
            cur_y = self.nose_point.y

            if self.nose_direction == 0:
                cur_x += i

            elif self.nose_direction == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.dead_ships = 0
        self.ships = []

        self.taken_dots = []
        self.field = [["O"] * size for _ in range(size)]

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.taken_dots:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.taken_dots.append(cur)

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.taken_dots:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.taken_dots.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.taken_dots:
            raise BoardUsedException()

        self.taken_dots.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.durability -= 1
                self.field[d.x][d.y] = "X"
                if ship.durability == 0:
                    self.dead_ships += 1
                    self.contour(ship, verb=True)
                    print("Ship destroyed!")
                    return False
                else:
                    print("Ship wounded")
                    return True

        self.field[d.x][d.y] = "."
        print("Miss")
        return False

    def begin(self):
        self.taken_dots = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"AI move: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Your move is: ").split()

            if len(cords) != 2:
                print(" Enter 2 coordinate! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Enter number! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size),
                                randint(0, self.size)),
                            l,
                            randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Your board:")
            print(self.us.board)
            print("-" * 20)
            print("AI's board:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                repeat = self.us.move()
            else:
                print("-" * 20)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.dead_ships == 7:
                print("-" * 20)
                print("You win!")
                break

            if self.us.board.dead_ships == 7:
                print("-" * 20)
                print("AI win!")
                break
            num += 1

    def start(self):
        self.loop()


if __name__ == '__main__':
    g = Game()
    g.start()
