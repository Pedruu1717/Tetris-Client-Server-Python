from pip._vendor.msgpack.fallback import xrange
from playsound import playsound

import game


class GameBoard:
    def __init__(self):
        self._board = [[0 for x in xrange(game.cols)]
                       for y in xrange(game.rows)]
        self._board += [[1 for x in xrange(game.cols)]]

    @property
    def board(self):
        """ Metodo que devolve o bord  """
        return self._board

    @board.setter
    def board(self, board):
        self._board = board


    def rotate_clockwise(self, shape):
        """ Método que retorna uma peça rodada"""
        return [[shape[y][x]
                 for y in xrange(len(shape))]
                for x in xrange(len(shape[0]) - 1, -1, -1)]

    def check_collision(self, shape, offset):
        """ Verifica se existe uma colisão no tabuleiro e retorna um boleano"""
        off_x, off_y = offset
        for cy, row in enumerate(shape):
            for cx, cell in enumerate(row):
                try:
                    if cell and self._board[cy + off_y][cx + off_x]:
                        return True
                except IndexError:
                    return True
        return False

    def remove_row(self, row):
        """ Método que elimina uma linha do tabuleiro"""
        del self._board[row]
        return [[0 for i in xrange(game.cols)]] + self._board

    def join_matrixes(self, mat1, mat2, mat2_off):
        """ Método que junta duas matrizes """
        off_x, off_y = mat2_off
        for cy, row in enumerate(mat2):
            for cx, val in enumerate(row):
                mat1[cy + off_y - 1][cx + off_x] += val
        return mat1
