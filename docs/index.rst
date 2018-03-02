.. Cardenal documentation master file, created by
   sphinx-quickstart on Tue Feb 20 15:59:49 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cardenal
====================================

First advice
-----------------

If you are a person that have to run time demanding process or tests in some project and feel the need to notify events or logs easily to your cellphone, then you are in the right place.

If you don't but still feel courious about what Cardenal is... ok, just keep reading.

What it does?
-----------------

Cardenal is a TCP server (uses the library ZMQ_) that recives text messages (in an early future images too!) and forward them to a certain clients that have made suscription to a Telegram bot.

The server is coded entearly in python, but the clients could be for any language that supports ZMQ. A good start to know the alcance is check the `ZMQ lenguage Bindings`_

The first client was for python too and is the one that we use in this documentation for our examples. You can check the project in te GitHub repository here: cardenal-python-client_

About the name
-----------------

Cardenal is a bird from my region in Argentina. A very fancy bird. Here's the guy


.. only:: html

   .. figure:: _misc/cardenal.jpg
      :width: 300pt
      :align: center

The main reason of this name is that I usually take species of the fauna of my country for my projects.
Beside this, the idea of a bird sounds great for the purpose of this project.

Limitations
-----------------

Is not tested (yet) to work with high demanding enviroments like houndred of clients and thousend of messages.
The early concept should be used with a few persons and a few events and messages running in a local server, mostly for testing.
More intensive and demanding uses still being tested.

Getting started
----------------

1. Create your own bot
^^^^^^^^^^^^^^^^^^^^^^^^^^

The first step is create your own Telegram Bot with the help of the BotFather_.

Once you have the **token** you have to save it in some place that you know you wont lose it. We will need this later.

Should not be necesary any additional configuration besides a basic bot should be necesary to make this work.

Lets say, Cardenal only provide the interface between your code and your bot. The bot that you use is yours.
Cardenal it self is not a bot, is just a tool that uses the bot.


2. Install
^^^^^^^^^^^^^^^^^^^^^

In order to install Cardenal you can do the usual: ``python setup.py install``

The dependencies of the Cardenal package are:
 #. peewee_
 #. `python-telegram-bot`_
 #. pyzmq_


3. Run it
^^^^^^^^^^^^^^^^^^^^^

Once installed run the following code::

>>> from Cardenal.server import Cardenal
>>> BOT_KEY = 'your-bot-key'  # This is the one that we get in step 1
>>> DB_PATH = 'path/to/database.db'  # This is the sqlite database path where we'll store the users information
>>> server = Cardenal(BOT_KEY, DB_PATH)  # This will create the database and tables in case that doesn't exist yet
>>> server.run()  # This will start the server.

With the server running you should suscribe to the bot in your Telegram account.
If everything is right the bot will send you a messages with your data.


.. only:: html

   .. figure:: _misc/ex_01.gif
      :width: 250pt
      :align: center

4. Clients
^^^^^^^^^^^^^^^^^^^^

Cardenal server is coded in python, but the fact that we use the ZMQ library allows you to operate with clients for different lenguagges.
Any language that support the ZMQ library and allows to mount a PUB/SUB scheme if factible to function as Cardenal client.

For more information please go to section `Clients`

Here we have an example of how to send messages using the client `cardenal-python-client`_::


    >> from CardenalClient.client import CardenalClient
    >> cli = CardenalClient('localhost')  # This is because we are running the server localy
    >> user_id = 12345  # My telegram ID. Cardenal send you this when you log to the server (go to step 3)
    >> username = 'myUsername'  # Telegram Username
    >> cli.txt_msg('Message using my user ID', user_id=user_id)
    >> cli.txt_msg('Message using my username', username=username)

Voila!

.. only:: html

   .. figure:: _misc/ex_02.gif
      :width: 250pt
      :align: center


.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. _ZMQ: http://zeromq.org/
.. _cardenal-python-client: https://github.com/Bgeninatti/cardenal-python-client
.. _BotFather: https://core.telegram.org/bots#6-botfather
.. _`ZMQ lenguage Bindings`: http://zeromq.org/bindings:_start
.. _peewee: http://docs.peewee-orm.com/en/latest/
.. _`python-telegram-bot`: https://github.com/python-telegram-bot/python-telegram-bot
.. _pyzmq: https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/
