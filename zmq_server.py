import zmq
import json
from threading import Thread

from models import User, Notificacion

DEFAULT_COMMAND_PORT = 6666
DEFAULT_POLLER_TIMEOUT = 5


class CardenalZmqServer(object):

    def __init__(self,
                 command_port=DEFAULT_COMMAND_PORT,
                 command_poller_timeout=DEFAULT_POLLER_TIMEOUT,
                 autostart=True):

        self._context = zmq.Context()
        self._command_socket = self._context.socket(zmq.REP)
        self._command_socket.bind("tcp://*:{0}".format(command_port))
        self._command_poller = zmq.Poller()
        self._command_poller_timeout = command_poller_timeout
        self._command_poller.register(self._command_socket)

        # Bandera de parada para los Threads
        self._stop = True
        # Inicio thread de recepcion de comandos
        self.command_thread = Thread(target=self._recive_commands)
        if autostart:
            self.start()

    def start(self):
        self._stop = False
        self.command_thread.start()

    def stop(self):
        self._stop = True
        self.command_thread.join()
        self.command_thread = None
        self._command_socket.close()
        self._context.term()

    def _recive_commands(self):
        '''
            Tiene que recibir un diccionario json con las siguientes claves:
              user_id: int,
              username: text,
              msg: text
            Se debe especificar user_id o username. Si ambos están presentes se
            usa username
        '''
        while not self._stop:
            socks = self._command_poller.poll(self._command_poller_timeout)
            for socket, _ in socks:
                msg_string = socket.recv_string()
                try:
                    msg = json.loads(msg_string)
                except ValueError:
                    socket.send_string(json.dumps({
                        'status': 500,
                        'msg': "Error en formato del comando. No es compatible con el formato JSON"}))
                    continue
                if 'msg' not in msg.keys():
                    socket.send_string(json.dumps({
                        'status': 501,
                        'msg': "No se especifico un mensaje para la notificación."}))
                    continue

                if 'username' in msg.keys():
                    u = User.get(username=msg['username'])
                elif 'user_id' in msg.keys():
                    u = User.get(id=msg['user_id'])
                else:
                    socket.send_string(json.dumps({
                        'status': 502,
                        'msg': "No se especifico username o user_id."}))
                    continue

                try:
                    Notificacion.create(user=u, msg=msg['msg'])
                    socket.send_string(json.dumps({
                        'status': 200,
                        'msg': "Notificacion creada correctamente"}))
                except:
                    socket.send_string(json.dumps({
                        'status': 503,
                        'msg': "Hubo un error en la creación de la notificacion."}))
                    continue


if __name__ == '__main__':
    CardenalZmqServer()
