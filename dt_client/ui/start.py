from tkinter import Tk, Label, Button, Entry, CENTER, N
from stubs.ClientStub import ClientStub
import ui

from playsound import playsound

"""
Classe Start

Inicializa a interface gráfica do cliente através do Tkinter.
"""


class Start:
    """client ui front-end"""

    def __init__(self, window: Tk, canvas_size: tuple):
        self._window = window
        self._window2 = None
        self._canvas = None
        self._canvas_size = canvas_size
        self._window.geometry = '800x800'
        self._enter_game_button = None
        self._leave_button = None
        self._play_game_button = None
        self._connect_button = None
        self._client_stub = ClientStub()
        self._rotate_button = None
        self._move_right_button = None
        self._move_left_button = None
        self._move_down_button = None
        self._name = None
        self._leave = None

    def enter_game(self):
        """Mostra um menu que possibilita o cliente connectar-se com o servidor"""
        enter_name = Entry(self._window, justify='center')
        enter_name.insert(0, "Player Name")
        enter_name.place(relx=0.5, rely=0.2, anchor=N)

        self._connect_button = Button(self._window, text="Connect", justify='center', height=7, width=7, bg="#1d3557",
                                      fg='white', borderwidth=3, command=lambda: self.send_name(enter_name.get()))

        self._connect_button.config(height=3, width=17)
        self._connect_button.place(relx=0.5, rely=0.5, anchor=CENTER)

    def main_program_default(self):
        """Mostra o menu com butões para que o cliete possa interagir com o jogo"""
        self._window2 = Tk()

        self._window2.resizable(width=800, height=800)
        text = 'Welcome to TetrisSD: {} '.format(self._name)
        initial_text = Label(self._window2, text=text)
        initial_text.grid(column=2, row=0)
        self._enter_game_button = Button(self._window2, text="Enter Game", justify='center', height=7, width=7,
                                         bg="#1d3557", fg='white', borderwidth=3, command=self.enter_game)
        self._play_game_button = Button(self._window2, text="Play Game", justify='center', height=7, width=7,
                                        bg="#92140c", fg='white', borderwidth=3, command=self.play_game)
        self._enter_game_button.grid(column=2, row=4, padx=15, pady=15)
        self._play_game_button.grid(column=2, row=8, padx=15, pady=15)
        self._enter_game_button.config(height=3, width=20)
        self._play_game_button.config(height=3, width=20)

        self._rotate_button = Button(self._window2, text="Rotate", justify='center', height=7, width=7,
                                     bg="#00cc00", fg='white', borderwidth=3, command=self.rotate_piece)
        self._rotate_button.grid(column=2, row=16, padx=15, pady=15)
        self._rotate_button.config(height=3, width=7)

        self._move_right_button = Button(self._window2, text="->", justify='center', height=7, width=7,
                                         bg="#ff8000", fg='white', borderwidth=3, command=lambda: self.move(1), )
        self._move_right_button.grid(column=3, row=20, padx=15, pady=15)
        self._move_right_button.config(height=3, width=7)

        self._move_left_button = Button(self._window2, text="<-", justify='center', height=7, width=7,
                                        bg="#ff8000", fg='white', borderwidth=3, command=lambda: self.move(-1), )
        self._move_left_button.grid(column=1, row=20, padx=15, pady=15)
        self._move_left_button.config(height=3, width=7)

        self._move_down_button = Button(self._window2, text="V", justify='center', height=7, width=7,
                                        bg="#7f00ff", fg='white', borderwidth=3, command=lambda: self.drop(True), )
        self._move_down_button.grid(column=2, row=20, padx=15, pady=15)
        self._move_down_button.config(height=3, width=7)

        self._leave_button = Button(self._window2, text="LEAVE GAME", justify='center', height=7, width=7,
                                    bg="#7f00ff", fg='white', borderwidth=3, command=self.leave_game)
        self._leave_button.grid(column=2, row=12, padx=15, pady=15)
        self._leave_button.config(height=3, width=20)

        # Jogar utilizando o teclado do computador

        self._window2.bind(ui.ROTATE_STONE, self.rotate_piece)
        self._window2.bind(ui.MOVE_DOWN, lambda event, a=True: self.drop(a))
        self._window2.bind(ui.MOVE_LEFT, lambda event, a=-1: self.move(a))
        self._window2.bind(ui.MOVE_RIGHT, lambda event, a=1: self.move(a))
        self._window2.bind(ui.PLAY_AGAIN, self.play_again)
        self._window2.bind(ui.QUIT, self.leave_game)
        self._window2.after(1, lambda: self._window2.focus_force())
        self._window2.mainloop()

    def leave_game(self):
        """ Envia um pedido ao client stub informando que quer sair do jogo"""
        print('Leaving game...')
        self._client_stub.leave_game()

    def send_name(self, name: str):
        """
        Lê uma string da conexão aberta atual e envie
        ao servidor para verificar se ele ainda não existe
        """

        self._name = self._client_stub.server_connect(name)
        self.main_program_default()

    def play_game(self):
        """
        Envia um pedido ao client stub informando que quer jogar
        """
        self._client_stub.send_play_game_msg()

    def rotate_piece(self, _event=None):
        """
        Envia um pedido ao client stub informando que quer rodar a peça .
        """
        self._client_stub.rotate_clockwise()

    def move(self, x):
        """
         Envia um pedido ao client stub informando que quer mover a peça( para esquerda ou para direita)
        """
        self._client_stub.move(x)

    def drop(self, manual: bool):
        """
        Envia um pedido ao client stub informando que quer apressar a descida da peça.
        """
        self._client_stub.drop(manual)

    def play_again(self, _event=None):
        """
        Envia um pedido ao client stub informando que quer jogar novamente.
        """
        self._client_stub.play_again()
