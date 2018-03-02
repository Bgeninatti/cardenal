import unittest
import zmq
from zmq_server import CardenalZmqServer


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
            msg = json.dumps({'msg': msg, 'user_id': user_id})
        elif username is not None:
            msg = json.dumps({'msg': msg, 'username': username})
        else:
            raise ValueError("Se debe especificar username o user_id como" +
                             "parámetros")

        self.socket.send_string(msg)
        socks = self.poller.poll(10)


class ZMQServerTest(unittest.TestCase):

    def setUp(self):
        self.server = CardenalZmqServer()
        self.client = MockClient()

    def tearDown(self):
        self.server.stop()
        self.client.stop()

    def test_empty(self):
        msgs = self.server.check_msgs()
        self.assertEqual(len(msgs), 0)

    def test_500_not_json(self):
        self.client.socket.send_string("asd")
        msgs = self.server.check_msgs()
        rta = self.client.socket.recv_json()
        self.assertEqual(rta['status'], 500)

    def test_500_not_dict(self):
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
