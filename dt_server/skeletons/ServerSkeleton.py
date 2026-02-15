import game
import pygame
import threading
import zmq

from game.game import Game
from game.player import Player

"""
Classe ServerSkeleton

Recebe pedidos do cliente, pelo seu stub, e devolve-lhe respostas de indicação do estado do jogo
e quais as funções que devem ser executadas do lado do cliente.
"""


class ServerSkeleton:
    def __init__(self):
        self._socket2 = None
        self._address = game.ADDRESS
        self._port2 = game.PORT2
        self._app = Game()
        self._game_thread = threading.Thread(target=self._app.run)
        self._player_thread = None
        self._game_started = False
        self._lock = threading.Lock()

    def run(self) -> None:
        """
        Cria um canal de comunicação com um socket do tipo Reply.
        """
        print('Server Running...')
        context = zmq.Context()

        self._socket2 = context.socket(zmq.REP)
        self._socket2.bind("tcp://" + self._address + ":" + self._port2)
        while 1:
            with self._lock:
                if self._app.users_list.is_empty() and self._game_started:
                    pass
                else:
                    self.receive()

    def receive(self) -> None:
        """
        Recebe os pedidos do cliente e processa-os com a função 'eval()'.
        """
        pygame.event.pump()
        response2 = self._socket2.recv_json()  # recebe string do cliente indicando o seu pedido (funçao).
        print('Socket recebeu.')
        print('Resposta Socket ->', response2)

        function2 = response2['function']
        if function2:
            eval(function2)

    def add_user(self, name_user: str) -> None:
        """
        Recebe o nome do jogador e verifica se é correto.
        Caso correto: envia resposta com o objeto do tipo Player
        Caso errado: envia resposta com 'None'
        Quando o cliente recebe 'None' neste contexto, ele envia denovo um pedido com o mesmo
         nome acrescentando um 2 no final. (Nome_do_jogador2).

        :param name_user -> Nome do jogador.
        """
        player = Player(name_user)
        if self._app.users_list.is_empty():
            self._app.users_list.add(player)
            print('Server: Your name is valid. Now click "Play Game".')
            self._socket2.send_json({'player': player.name})
        else:
            add = True
            i = 0
            while i < len(self._app.users_list):  # NAO APAGAR
                p = self._app.users_list.itens.__getitem__(i)
                if p.name == str(name_user):
                    add = False
                    break
                i += 1
            if add:
                self._app.users_list.add(player)
                print('Server: Your name is valid. Now click "Play Game".')
                self._socket2.send_json({'player': player.name})
            else:
                print('Server: The user already exists. Named Generated Automatically.')
                self._socket2.send_json({'player': None})

    def exec_game(self) -> None:
        """
        Inicia a app do jogo através de uma thread e envia para o cliente as especificações da UI,
        mais propriamente do pygame.
        :return:
        """
        if not self._game_started:
            self._game_thread.start()
            self._game_started = True
        json_msg = \
            {'display': 'pygame.display.set_mode((' + str(self._app._width) + ',' + str(self._app._height) + '))'}
        self._socket2.send_json(json_msg)

    def send_data(self, player_name: str) -> None:
        """
        Método para enviar constantemente o estado do jogo e informação gráfica para o cliente
        :param player_name:
        """
        player = None
        for p in self._app.users_list.itens:  # Encontrar o jogador que mandou o pedido.
            if player_name == p.name:
                player = p
                break

        if self._app.current_player:
            current_player_name = self._app._current_player.name
        else:
            current_player_name = None
        json_msg = {
            'current_player': current_player_name,
            'gameover': self._app._gameover,
            'paused': self._app.paused,
            'background_image': 'pygame.image.load("ui/background.bmp").convert()',
            'screen': 'pygame.display.set_mode((self.width, self.height))',
            'screen.blit': 'self.screen.blit(background_image, [0, 0])',
            'score': self._app.score,
            'highest_score': self._app._highest_score,
            'max_lines': self._app._max_lines,
            'max_player_name': self._app._max_player_name,
            'center_msg': 'self.center_msg("""Game Over! Try Again!\nMax Lines: %d\n Winner: %s\n'
                          'Press space to continue""" % (max_lines, max_player_name))',
            'rlim': self._app.rlim,
            'height': self._app._height,
            'disp_msg1': 'self.disp_msg("Next:", ( rlim + 18,2))',
            'disp_msg2': 'self.disp_msg("""Level: %d""" % (level), (rlim + 18, '
                         '18 * 5))',
            'gameboard': self._app._gameboard._board,
            'draw_matrix1': 'self.draw_matrix(board, (0, 0))',
            'draw_matrix2': 'self.draw_matrix(stone,(stone_x, stone_y))',
            'draw_matrix3': 'self.draw_matrix(next_stone, (16 + 1, 2))',
            'lines': player.lines,
            'stone': self._app._stone,
            'stone_x': self._app._stone_x,
            'stone_y': self._app._stone_y,
            'clear_preview': 'self.clear_preview(stone, (16 + 1, 2))',
            'next_stone': self._app._next_stone,
            'quit': 'quit()',
            'level': self._app.level,
            'width': self._app._width,
            'default_font': 'pygame.font.Font(pygame.font.get_default_font(), 12)'
        }

        self._socket2.send_json({'function': 'self.update_ui(json_msg)', 'arg': json_msg})

    def rotate_piece(self) -> None:
        """
        Indica à aplicação (jogo) que deve ser rodada a peça atual.
        :return:
        """
        self._app.rotate_stone()
        self.send_default()

    def move(self, delta_x) -> None:
        """
        Indica à aplicação (jogo) que deve ser movida a peça atual. (direita ou esquerada).
        :return:
        """
        self._app.move(delta_x)
        self.send_default()

    def drop(self, manual) -> None:
        """
        Indica à aplicação (jogo) que deve ser movida a peça atual para baixo.
        :return:
        """
        self._app.drop(manual)
        self.send_default()

    def play_again(self) -> None:
        """
        Indica à aplicação (jogo) que um dos clientes quer jogar denovo (reiniciar o jogo).
        :return:
        """
        self._app.start_game()
        self.send_default()

    def send_default(self) -> None:
        """
        Método para enviar para o cliente uma mensagem sem informação.
        :return:
        """
        self._socket2.send_json({'status': 'ok'})

    def remove_user(self, name_user: str) -> None:
        """
        Indica à aplicação (jogo) que deve ser removido um jogador da lista (fila) de jogadores.
        :param name_user -> Nome do jogador.
        """
        for player in self._app.users_list.itens:
            print(player)
            if player.name == name_user:
                self._app.users_list.remove(player)
                break

        self._socket2.send_json({'status': 'ok'})
        print('Left game.')
