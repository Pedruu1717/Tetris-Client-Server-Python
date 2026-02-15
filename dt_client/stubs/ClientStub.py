import sys
import time

from playsound import playsound

import stubs, zmq, pygame, threading
from game.player import Player
import sound
from dt_server.game.gameboard import GameBoard

"""
   ClientStub

   Despacha os pedidos do cliente para o servidor .
   """


class ClientStub:

    def __init__(self):
        self._is_player_using_command: bool = False
        self.width = None
        self.height = None
        self.screen = None
        self.default_font = None
        self._request_update = False
        self._socket2 = None
        self._address = stubs.ADDRESS  # constantes provenientes do __init__
        self._port2 = stubs.PORT2
        self._player = None
        self._is_connected: bool = False

    def send_request(self, work_message) -> dict:
        """
        Método para enviar pedidos para o servidor e receber a resposta logo de seguida.
        :param work_message -> String que indica a função executar no servidor.

        :return:
        """
        self._socket2.send_json({'function': work_message})
        response = self._socket2.recv_json()

        return response

    def server_connect(self, name: str) -> Player:
        """
        Coneta ao servidor através da ligação que criou. Usa um socket do tipo Request.
        """

        context = zmq.Context()

        self._socket2 = context.socket(zmq.REQ)
        self._socket2.connect("tcp://" + self._address + ":" + self._port2)

        work_message = 'self.add_user("' + name + '")'
        response = self.send_request(work_message)

        player_name = response['player']
        if player_name:
            self._player = Player(player_name)
        else:
            work_message = 'self.add_user("' + name + '2")'
            response = self.send_request(work_message)
            player_name = response['player']
            self._player = Player(player_name)

        self._is_connected = True

        return self._player.name

    def send_play_game_msg(self) -> None:
        """
        Indicar ao servidor que o cliente está pronto para jogar (já inseriu o seu nome de utilizador).
        """
        # Envia msg para começar o jogo.
        work_message = 'self.exec_game()'
        response = self.send_request(work_message)
        eval(response['display'])
        self.send_msg_start_updating()

    def send_msg_start_updating(self) -> None:
        """
        Cliente começa a receber atualizações: sincronização.
        Envia pedido ao servidor para atualizar de forma constante.
        Faz uso do Timer do pacote Threading para evitar o uso de um ciclo while.
        """
        if self._is_connected:
            t = threading.Timer(1.0, self.send_msg_start_updating)
            t.start()

            # Envia msg para receber info (atualizar o UI do Cliente).
            work_message = 'self.send_data("' + self._player.name + '")'
            response = self.send_request(work_message)
            json_msg = response['arg']
            eval(response['function'])
            print('cliente')

    def update_ui(self, json_msg) -> None:
        """
         Método que está sempre a ser executado para atualizar a parte gráfica do cliente.
         É chamado no 'eval()' do método acima.
        """
        pygame.init()
        pygame.key.set_repeat(250, 25)
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
        pygame.event.pump()

        response = json_msg
        current_player = response['current_player']
        if current_player == self._player.name:
            self._player.is_player_turn = True
        else:
            self._player.is_player_turn = False

        rlim = response['rlim']
        self.height = response['height']
        self.width = response['width']
        score = response['score']
        highest_score = response['highest_score']
        gameboard = response['gameboard']
        board = gameboard

        max_lines = response['max_lines']
        max_player_name = response['max_player_name']

        gameover = response['gameover']
        paused = response['paused']
        background_image = eval(response['background_image'])
        self.screen = eval(response['screen'])
        self.default_font = eval(response['default_font'])
        screen_blit = response['screen.blit']

        center_msg = response['center_msg']

        disp_msg1 = response['disp_msg1']
        disp_msg2 = response['disp_msg2']

        draw_matrix1 = response['draw_matrix1']
        draw_matrix2 = response['draw_matrix2']
        draw_matrix3 = response['draw_matrix3']

        lines = response['lines']

        stone = response['stone']
        stone_x = response['stone_x']
        stone_y = response['stone_y']
        clear_preview = response['clear_preview']
        next_stone = response['next_stone']
        quit = response['quit']
        level = response['level']

        eval(screen_blit)
        if gameover:
            if self._player.lines > highest_score:  # O nº de linhas completadas é o score do jogador.
                highest_score = self._player.lines
            eval(center_msg)

        else:
            if paused:
                center_msg("Paused")
            else:
                pygame.draw.line(self.screen,
                                 (0, 0, 0),
                                 (rlim + 1, 0),
                                 (rlim + 1, self.height - 1))
                eval(disp_msg1)
                eval(disp_msg2)
                eval('self.disp_msg("Jogador:"+self._player.name, (rlim+18,170))')  # Nome do jogador.
                eval('self.disp_msg("Linhas:"+str(lines), (rlim+18,190))')  # Nº linhas completas pelo jogador.
                if self._player.is_player_turn:
                    eval('self.disp_msg("Sua vez de jogar",  (rlim+18,210))')
                eval(draw_matrix1)
                # Current shape.
                eval(draw_matrix2)
                # Draw black stone before next shape
                eval(clear_preview)
                # Next shape.
                eval(draw_matrix3)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                self.drop(False)
            elif event.type == pygame.QUIT:
                eval(quit)

    # Métodos q fazem o pedido para mover uma peça e para jogar novamente.
    #########################################################################################
    def rotate_clockwise(self):
        """
        O cliente indica ao jogador que quer rodar a peça.
        """
        if self._player.is_player_turn:
            self._is_player_using_command = True
            work_message = 'self.rotate_piece()'
            self.send_request(work_message)
            # Sound when rotates piece
            playsound(sound.LINE)
            self._is_player_using_command = False

    def move(self, delta_x):
        """
        O cliente indica ao jogador que quer mover a peça. (direita ou esquerda)
        """
        if self._player.is_player_turn:
            self._is_player_using_command = True
            work_message = 'self.move(' + str(delta_x) + ')'
            self.send_request(work_message)
            self._is_player_using_command = False

    def drop(self, manual):
        """
        O cliente indica ao jogador que quer mover a peça para baixo.
        """
        if self._player.is_player_turn:
            self._is_player_using_command = True
            if manual:
                manual = 'True'
            else:
                manual = 'False'
            work_message = 'self.drop(' + manual + ')'
            self.send_request(work_message)
            playsound(sound.LINE)
            self._is_player_using_command = False

    def play_again(self):
        """
        O cliente indica ao jogador que quer jogar denovo.
        """
        if self._player.is_player_turn:
            self._is_player_using_command = True
            work_message = 'self.play_again()'
            response = self.send_request(work_message)
            # Sound when resetting game.
            playsound(sound.GAMEOVER)
            self._is_player_using_command = False

    ##########################################################################################
    # Metodos da parte grafica.
    def disp_msg(self, msg, topleft):
        """
        Método que mostra uma mensagem no UI do cliente.
        """
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
        """
        Método que centra uma mensagem no UI do cliente.
        """
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x * 1.70,
                self.height // 2.7 - msgim_center_y + i * 25))

    def draw_matrix(self, matrix, offset):
        """
        Método que desenha uma matriz.
        """
        colors = [
            (0, 0, 0),
            (255, 85, 85),
            (100, 200, 115),
            (120, 108, 245),
            (255, 140, 50),
            (50, 120, 52),
            (146, 202, 73),
            (150, 161, 218)
        ]
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(
                            (off_x + x) *
                            18,
                            (off_y + y) *
                            18,
                            18,
                            18), 0)

    def clear_preview(self, matrix, offset):
        """
        Método que limpa a preview da próxima peça.
        """
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 0),
                        pygame.Rect(
                            (off_x + x) *
                            18,
                            (off_y + y) *
                            18,
                            18,
                            18), 0)

    def leave_game(self):
        """
        Método que é executado quando o jogador decide sair do jogo.
        É enviado ao servidor o pedido e depois o jogo remove-o da lista (fila) de jogadores.
        """
        self._is_connected = False
        work_message = 'self.remove_user("' + self._player.name + '")'
        self.send_request(work_message)
        print('Leaving game stub..')
        pygame.display.quit()
        pygame.quit()
        sys.exit()
