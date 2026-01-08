import pygame
from random import randint as rnd
from random import random as rnd_

ROWS = 13
COLS = 20
CELLW = 50
CELLH = 50
WINDOW_W, WINDOW_H = COLS * CELLW, ROWS * CELLH


class Board:
    def __init__(self, rows, cols, cellw, cellh, surface):
        self.rows = rows
        self.cols = cols
        self.cellw = cellw
        self.cellh = cellh
        self.board = [[None for _ in range(cols)] for __ in range(rows)]
        self.surface = surface
        self.cells = pygame.sprite.Group()

    def __getitem__(self, key):
        row, col = key
        return self.board[row][col]

    def __setitem__(self, key, value):
        row, col = key
        self.cells.remove(self.board[row][col])
        self.cells.add(value)
        self.board[row][col] = value

    def draw(self):
        self.cells.draw(self.surface)

    def update(self):
        self.cells.update()

    def showall(self):
        for row in range(1, self.rows-1):
            for col in range(1, self.cols-1):
                self.board[row][col].isopened = True



class Cell(pygame.sprite.Sprite):
    def __init__(self, w, h, row, col, bg, icon="\U0001f4a3", color=(255, 255, 255)):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(col * w, row * h))
        self.w = w
        self.h = h
        self.row = row
        self.col = col
        self.bg = bg
        self.color = color
        self.text = icon

        self.font_size = min(self.w, self.h)
        self.font_size = int(self.font_size * 0.5) if icon.isdigit() else  self.font_size
        self.font = pygame.font.SysFont("Segoe UI Emoji", self.font_size)

        self.isactive = False
        self.isopened = False

    def update(self):
        self.image.fill(self.bg)
        if self.isopened:
            text_surf = self.font.render(self.text, True, self.color)
            self.image.blit(
                text_surf, text_surf.get_rect(center=self.image.get_rect().center)
            )
        if self.isactive:
            pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 3)


class Game:
    SPROCESS = 0
    SFAIL = 1
    SSUCCESS = 2

    WALL = -2
    START = -3
    FINISH = -4
    BOMB = -1
    EMPTY = 0
    SYM = {
        WALL: "\U0001f9f1",
        START: "\U0001f6a9",
        FINISH: "\U0001f3c1",
        BOMB: "\U0001f4a5",
    }

    def __init__(self, rows, cols, cellw, cellh, surface):
        self.rows = rows
        self.cols = cols
        self.cellw = cellw
        self.cellh = cellh
        self.surface = surface
        self.prepare_map()
        self.make_board()
        self.state = Game.SPROCESS

    def prepare_map(self):
        self.map = [[Game.EMPTY for _ in range(self.cols)] for __ in range(self.rows)]
        # розставляємо стіни
        for i in range(self.cols):
            self.map[0][i] = Game.WALL
            self.map[self.rows - 1][i] = Game.WALL

        for i in range(self.rows):
            self.map[i][0] = Game.WALL
            self.map[i][self.cols - 1] = Game.WALL

        # розтавляємо бомби
        count = 0
        hardness = int(self.rows * self.cols * 0.05)
        while count < hardness:
            row = rnd(1, self.rows - 2)
            col = rnd(1, self.cols - 2)
            if self.map[row][col] != Game.BOMB:
                self.map[row][col] = Game.BOMB
                count += 1

        # розтавляємо підказки
        moves = ((-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1), (0, -1), (0, 1))
        for row in range(1, self.rows - 1):
            for col in range(1, self.cols - 1):
                if self.map[row][col] != Game.BOMB:
                    count = 0
                    for vert, hor in moves:
                        if (
                            row + vert >= 1
                            and row + vert <= self.rows - 2
                            and col + hor >= 1
                            and col + hor <= self.cols - 2
                            and self.map[row + vert][col + hor] == Game.BOMB
                        ):
                            count += 1
                    self.map[row][col] = count

        # Старт та фініш
        if rnd_() >= 0.5:
            self.srow = 0
            self.frow = self.rows - 1
        else:
            self.frow = 0
            self.srow = self.rows - 1
        self.scol = rnd(1, self.cols - 2)
        self.fcol = rnd(1, self.cols - 2)
        self.crow = self.srow
        self.ccol = self.scol
        self.map[self.srow][self.scol] = Game.START
        self.map[self.frow][self.fcol] = Game.FINISH
        self.orow = self.crow
        self.ocol = self.ccol

    def make_board(self):
        self.msg_surf = None
        self.board = Board(self.rows, self.cols, self.cellw, self.cellh, self.surface)
        for row in range(self.rows):
            for col in range(self.cols):
                color = (rnd(100, 132), rnd(132, 164), rnd(164, 196))
                sym = Game.SYM.get(self.map[row][col], self.map[row][col])
                cell = Cell(self.cellw, self.cellh, row, col, color, str(sym), (0,0,0))
                if self.map[row][col] < Game.BOMB:
                    cell.isopened = True
                self.board[row, col] = cell
        self.board[self.crow, self.ccol].isactive = True

    def message(self, text, color):
        font_size = 100
        while 1:
            font = pygame.font.SysFont("Terminal", font_size)
            if font.size(text)[0] > self.surface.get_width() - 20:
                font_size -= 5
            else:
                break
        self.msg_surf = font.render(text, True, color)

    def draw(self):
        self.board.draw()
        if self.msg_surf:
            rect = self.msg_surf.get_rect(center=self.surface.get_rect().center)
            self.surface.blit(self.msg_surf, rect)

    def update(self):
        self.board.update()

    def keypress(self, key):
        if self.state == Game.SPROCESS:
            self.ocol = self.ccol
            self.orow = self.crow
            if key == pygame.K_UP:
                self.crow = self.crow - 1
            elif key == pygame.K_DOWN:
                self.crow = self.crow + 1
            elif key == pygame.K_LEFT:
                self.ccol = self.ccol - 1
            elif key == pygame.K_RIGHT:
                self.ccol = self.ccol + 1
            # elif key == pygame.K_SPACE:
            #     self.board[self.crow, self.ccol].isopened = True

            if (
                self.ccol < 0
                or self.ccol >= self.cols
                or self.crow < 0
                or self.crow >= self.rows
                or self.map[self.crow][self.ccol] == Game.WALL
            ):
                self.ccol = self.ocol
                self.crow = self.orow
                return

            if self.crow == self.frow and self.ccol == self.fcol:
                self.board.showall()
                self.message("Ви вижили! ENTER щоб спробувати заново!", (255,255,255))
                self.state = Game.SSUCCESS

            if self.map[self.crow][self.ccol] == Game.BOMB:
                self.board.showall()
                self.message("Ви програли! ENTER щоб спробувати заново!", (255,255,255))
                self.state = Game.SFAIL

            if self.ocol != self.ccol or self.orow != self.crow:
                self.board[self.orow, self.ocol].isactive = False
                self.board[self.crow, self.ccol].isactive = True
                self.board[self.crow, self.ccol].isopened = True

        elif self.state == Game.SSUCCESS or self.state == Game.SFAIL:
            if key == pygame.K_RETURN:
                self.prepare_map()
                self.make_board()
                self.state = Game.SPROCESS




pygame.init()
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("САПЕР")
clock = pygame.time.Clock()

game = Game(ROWS, COLS, CELLW, CELLH, screen)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            game.keypress(event.key)

    game.update()
    game.draw()
    
    pygame.display.flip()

    clock.tick(15)

pygame.quit()
