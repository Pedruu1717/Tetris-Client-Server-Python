from random import randrange as rand
import game


class Shape:
    def __init__(self):

        self._shape = game.tetris_shapes[rand(len(game.tetris_shapes))]
        self._next_shape = game.tetris_shapes[rand(len(game.tetris_shapes))]
        self._shape_x = int(game.cols / 2 - len(self._shape[0]) / 2)
        self._shape_y = 0

    @property
    def shape(self):
        """Return a all shapes"""
        return self._shape

    @property
    def next_shape(self):
        """Return a next shape"""
        return self._next_shape

    @property
    def shape_x(self):
        """Return a shape in x position"""
        return self._shape_x

    @property
    def shape_y(self):
        """Return a shape in y position"""
        return self._shape_y
