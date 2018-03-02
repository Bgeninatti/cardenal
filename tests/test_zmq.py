import unittest
import zmq
from Cardenal.zmq_server import CardenalZmqServer


class MockClient(object):

    def __init__(self, port=6666):
        self.ip = 'localhost'
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect('tcp://%s:%d' % (self.ip, self.port))

    def stop(self):
        self.socket.close()
        self.context.term()

    def send_msg(self, msg, user_id=None, username=None):
        if user_id is not None:
            msg = {'msg': msg, 'user_id': user_id}
        elif username is not None:
            msg = {'msg': msg, 'username': username}
        else:
            raise ValueError("Se debe especificar username o user_id como" +
                             "parámetros")

        self.socket.send_json(msg)


class ZMQServerTest(unittest.TestCase):

    def setUp(self):
        self.client = MockClient()

    def tearDown(self):
        self.client.stop()

    @classmethod
    def setUpClass(cls):
        cls.server = CardenalZmqServer()

    @classmethod
    def tearDownClass(cls):
        cls.server._command_socket.close()
        cls.server._context.term()

    def test_500(self):
        self.client.socket.send_json("asd")
        msgs = self.server.check_msgs()
        rta = self.client.socket.recv_json()
        self.assertEqual(rta['status'], 500)

    def test_501(self):
        self.client.socket.send_json({'a': 123})
        msgs = self.server.check_msgs()
        rta = self.client.socket.recv_json()
        self.assertEqual(rta['status'], 501)

    def test_502(self):
        self.client.socket.send_json({'msg': 123})
        msgs = self.server.check_msgs()
        rta = self.client.socket.recv_json()
        self.assertEqual(rta['status'], 502)

    def test_200(self):
        self.client.socket.send_json({'msg': 123, 'user_id': 1})
        msgs = self.server.check_msgs()
        rta = self.client.socket.recv_json()
        self.assertEqual(rta['status'], 200)
