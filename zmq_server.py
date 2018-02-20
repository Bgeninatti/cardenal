import zmq
import json

DEFAULT_COMMAND_PORT = 6666
DEFAULT_POLLER_TIMEOUT = 5


class CardenalZmqServer(object):

    def __init__(self,
                 command_port=DEFAULT_COMMAND_PORT,
                 command_poller_timeout=DEFAULT_POLLER_TIMEOUT):

        self._context = zmq.Context()
        self._command_socket = self._context.socket(zmq.REP)
        self._command_socket.bind("tcp://*:{0}".format(command_port))
        self._command_poller = zmq.Poller()
        self._command_poller_timeout = command_poller_timeout
        self._command_poller.register(self._command_socket)

    def stop(self):
        self._command_socket.close()
        self._context.term()

    def check_msgs(self):
        '''
            Tiene que recibir un diccionario json con las siguientes claves:
              user_id: int,
              username: text,
              msg: text
            Se debe especificar user_id o username. Si ambos están presentes se
            usa username
        '''
        socks = self._command_poller.poll(self._command_poller_timeout)
        msgs_buffer = []
        for socket, _ in socks:
            try:
                msg = socket.recv_json()
                if type(msg) is not dict:
                    raise TypeError
            except (json.decoder.JSONDecodeError, TypeError) as e:
                socket.send_string(json.dumps({
                    'status': 500,
                    'msg': "Error en formato del comando."}))
                continue
            if 'msg' not in msg.keys():
                socket.send_string(json.dumps({
                    'status': 501,
                    'msg': "No se especifico un mensaje para la notificación."
                }))
                continue

            if all((k not in ('username', 'usernames', 'user_id', 'users_ids') for k in msg.keys())):
                socket.send_string(json.dumps({
                    'status': 502,
                    'msg': 'No se especifico ningún destinatario para el ' +
                    'mensaje.'}))
                continue
            socket.send_string(json.dumps({
                'status': 200,
                'msg': "Notificacion creada correctamente"}))
            msgs_buffer.append(msg)
        return msgs_buffer
