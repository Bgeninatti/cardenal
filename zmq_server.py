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

            if 'username' not in msg.keys() and 'user_id' not in msg.keys():
                socket.send_string(json.dumps({
                    'status': 502,
                    'msg': "No se especifico username o user_id."}))
                continue
            socket.send_string(json.dumps({
                'status': 200,
                'msg': "Notificacion creada correctamente"}))
            msgs_buffer.append(msg)
        return msgs_buffer
