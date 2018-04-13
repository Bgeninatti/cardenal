import zmq
import json
import logging
from threading import Thread
from queue import Queue


class CardenalZmqServer(object):

    def __init__(self,
                 command_port=6666,
                 command_poller_timeout=5,
                 log_lvl='INFO'):

        self.logger = logging.getLogger('Cardenal.zmq')
        self.logger.setLevel(log_lvl)
        self._stop = False
        self._command_port = command_port
        self.msgs_queue = Queue()
        self._context = zmq.Context()
        self._command_socket = self._context.socket(zmq.REP)
        self._command_socket.bind("tcp://*:{0}".format(self._command_port))
        self._command_poller = zmq.Poller()
        self._command_poller.register(self._command_socket)
        self._command_poller_timeout = command_poller_timeout
        self._msgs_thread = Thread(target=self._keep_checking)

    def start(self):
        self._msgs_thread.start()

    def stop(self):
        self._stop = True
        self._command_socket.close()
        self._context.term()
        self._msgs_thread.join()

    def check_msgs(self):
        """
            Tiene que recibir un diccionario json con las siguientes claves:
              generator: text,
              msg: text
            Se debe especificar user_id.
        """
        msgs = []
        socks = self._command_poller.poll(self._command_poller_timeout)
        for socket, _ in socks:
            try:
                msg = socket.recv_json()
                if type(msg) is not dict:
                    raise TypeError
            except (json.decoder.JSONDecodeError, TypeError) as e:
                socket.send_string(json.dumps({
                    'status': 500,
                    'msg': "Error en formato del comando."}))
                self.logger.error("ERROR 500: Error en formato del comando.")
                continue

            if 'msg' not in msg.keys():
                socket.send_string(json.dumps({
                    'status': 501,
                    'msg': "No se especificó un mensaje para la notificación."
                }))
                self.logger.error("ERROR 501: No se especificó un mensaje " +
                                  "para la notificación.")
                continue

            socket.send_string(json.dumps({
                'status': 200,
                'msg': "Notificación creada correctamente"}))
            msgs.append(msg)
        return msgs

    def _keep_checking(self):
        while not self._stop:
            msgs = self.check_msgs()
            if len(msgs):
                self.logger.info("Se crearon {} notificaciones".format(len(msgs)))
            for m in msgs:
                self.msgs_queue.put(m)
