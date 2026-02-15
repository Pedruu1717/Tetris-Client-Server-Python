
import game
import pygame
import sys

from game.gameboard import GameBoard
from game.shape import Shape as Shape
from skeletons.queue import Queue


class Game:
    def __init__(self):
        self._users_list = Queue()
        self._max_lines: int = 0
        self._max_player_name: str = ''
        self._current_player = None
        self._first_shape = True
        self._gameboard = None
        self._gameover = False
        self._board = None
        self._stone = None
        self._next_stone = None
        self._stone_x = None
        self._stone_y = None
        self._highest_score = 0  # Não está a ser usado.
        self._width = game.cell_size * (game.cols + 6)
        self._height = game.cell_size * game.rows
        self.rlim = game.cell_size * game.cols

        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.screen = pygame.display.set_mode((self._width, self._height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self.background_image = pygame.image.load("game/background.bmp").convert()
        self.init_game()

    def get_players_lines(self):
        lista = []
        for p in self.users_list.itens:
            lista.append([p.name, p.lines])

        return lista  # [[Pedro,1],[Salif,2],...]

    def generate_shape(self):
        """ Método que gera uma nova peça """
        shape = Shape()
        if self._first_shape:
            self._stone = shape.shape
        else:
            self._stone = self._next_stone[:]

        self._next_stone = shape.next_shape
        self._stone_x = shape.shape_x
        self._stone_y = shape.shape_y
        self._first_shape = False
        if self._gameboard.check_collision(self._stone, (self._stone_x, self._stone_y)):
            self._gameover = True


    def init_game(self):
        """ Método que possui as variáveis do tabuleiro e pontuação """
        self._gameboard = GameBoard()
        self._board = self._gameboard.board
        self.generate_shape()
        self.level = 1
        self.score = 0
        self.lines = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        """ Método que formata as mensagens no tabuleiro """
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(
                    line,
                    False,
                    (255, 255, 255),
                    (0, 0, 0)),
                (x, y))
            y += 14

    def center_msg(self, msg):
        """ Método que centra as mensagens no tabuleiro """
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self._width // 2 - msgim_center_x * 1.70,
                self._height // 2.7 - msgim_center_y + i * 25))

    def draw_matrix(self, matrix, offset):
        """ Método que desenha a matriz no tabuleiro """
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        game.colors[val],
                        pygame.Rect(
                            (off_x + x) *
                            game.cell_size,
                            (off_y + y) *
                            game.cell_size,
                            game.cell_size,
                            game.cell_size), 0)

    def clear_preview(self, matrix, offset):
        """ Método que limpa a preview da peça seguinte """
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 0),
                        pygame.Rect(
                            (off_x + x) *
                            game.cell_size,
                            (off_y + y) *
                            game.cell_size,
                            game.cell_size,
                            game.cell_size), 0)

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self._current_player.lines += n  # Aumenta o nº de linhas completas pelo jogador q acabou de jogar.

        for player in self.users_list.itens:
            print(player.name, player.lines)

        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1
            newdelay = 1000 - 50 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT + 1, newdelay)

    def move(self, delta_x):
        """ Método que move uma peça no tabuleiro conforme o delta_x: 1, -1 """
        if not self._gameover and not self.paused:
            new_x = self._stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > game.cols - len(self._stone[0]):
                new_x = game.cols - len(self._stone[0])
            if not self._gameboard.check_collision(self._stone, (new_x, self._stone_y)):
                self._stone_x = new_x

    def quit(self):
        """ Método que encerra o jogo """
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self, manual):
        """ Método que move uma peça para baixo """
        if not self._gameover and not self.paused:
            self.score += 1 if manual else 0
            self._stone_y += 1
            if self._gameboard.check_collision(self._stone, (self._stone_x, self._stone_y)):
                self._board = self._gameboard.join_matrixes(
                    self._board,
                    self._stone,
                    (self._stone_x, self._stone_y))

                self.generate_shape()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self._board[:-1]):
                        if 0 not in row:
                            self._board = self._gameboard.remove_row(i)
                            cleared_rows += 1
                            self._gameboard._board = self._board
                            break
                    else:
                        break

                self.add_cl_lines(cleared_rows)
                self._current_player = self.users_list.pop()  # Retirar do inicio fila quando for a vez do próximo jogador
                self.users_list.add(self._current_player)  # e inserir no fim da fila.

                return True
        return False

    def insta_drop(self):
        """ Método que move uma peça para baixo automaticamente """
        if not self._gameover and not self.paused:
            while (not self.drop(True)):
                pass

    def rotate_stone(self):
        """ Método que roda uma peça """
        if not self._gameover and not self.paused:
            new_stone = self._gameboard.rotate_clockwise(self._stone)
            if not self._gameboard.check_collision(new_stone, (self._stone_x, self._stone_y)):
                self._stone = new_stone

    def toggle_pause(self):
        """ Método que pausa o jogo """
        self.paused = not self.paused

    def start_game(self):
        """ Método que inicializa o jogo """
        if self._gameover:
            self.init_game()
            self._gameover = False

    def run(self):
        """ Método que corre o jogo """
        self._current_player = self._users_list.peek()
        self._gameover = False
        self.paused = False

        while 1:
            if self._users_list.is_empty():
                self._gameover = True

            self.screen.blit(self.background_image, [0, 0])

            if self._gameover:
                for player in self.users_list.itens:
                    if player.lines > self._max_lines:
                        self._max_lines = player.lines
                        self._max_player_name = player.name
                self.center_msg("""Game Over! Try Again!\nMax Lines: %d\n Winner: %s\n
        Press space to continue""" % (self._max_lines, self._max_player_name))
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    pygame.draw.line(self.screen,
                                     (0, 0, 0),
                                     (self.rlim + 1, 0),
                                     (self.rlim + 1, self._height - 1))
                    self.disp_msg("SERVER\nNext:", (
                        self.rlim + game.cell_size,
                        2))
                    self.disp_msg("Score: %d\n\nLevel: %d\
        \nLines: %d" % (self.score, self.level, self.lines),
                                  (self.rlim + game.cell_size, game.cell_size * 5))
                    self.draw_matrix(self._board, (0, 0))
                    # Current shape.
                    self.draw_matrix(self._stone,
                                     (self._stone_x, self._stone_y))
                    # Draw black stone before next shape
                    self.clear_preview(self._stone, (game.cols + 1, 2))
                    # Next shape.
                    self.draw_matrix(self._next_stone, (game.cols + 1, 2))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()

    @property
    def users_list(self):
        """ Método que retorna a lista de jogadores """
        return self._users_list

    @property
    def current_player(self):
        """ Método que retorna o jogador atual """
        return self._current_player
