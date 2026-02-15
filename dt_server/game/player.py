class Player:
    def __init__(self, name: str):
        self._name = name
        self._lines: int = 0
        self._is_player_turn: bool = False

    @property
    def name(self):
        """Retorna o nome do jogador"""
        return self._name

    @property
    def lines(self):
        """Retorna as linhas do jogador"""
        return self._lines

    @lines.setter
    def lines(self, x: int):
        """Set a new player lines"""
        self._lines += x

    @property
    def is_player_turn(self):
        """Retorna Vez do jogador, se for true é a sua vez de jogar
           caso contrário não é a sua vez de jogar """
        return self._is_player_turn

    @is_player_turn.setter
    def is_player_turn(self, turn):
        """Altera o estado do jagador colocando true se for a sua vez de jogar e false caso não seja"""
        self._is_player_turn = turn
