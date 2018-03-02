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

Once you have the **token** add it to the config file in `config/cardenal.conf` under the variable name ``bot_token``.

Should not be necesary any additional configuration besides a basic bot should be necesary to make this work.

Lets say, Cardenal only provide the interface between your code and your bot. The bot that you use is yours. Cardenal it self is not a Bot.


2. Run it
^^^^^^^^^^^^^^^^^^^^^

To run Cardenal localy, in a unix console run::

    $ cd <path-to-cardenal>
    $ pyvenv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    $ python3 models.py
    $ python3 cardenal.py

With ``cardenal.py`` running you should suscribte to the bot in your Telegram account.
If everything is right the bot will send you a messages with your data.


.. only:: html

   .. figure:: _misc/ex_01.gif
      :width: 250pt
      :align: center

3. Clients
^^^^^^^^^^^^^^^^^^^^

El servidor Cardenal está escrito en Python, aunque su estructura permite operar con clientes escritos en distintos lenguajes.
Cualquier lenguaje que soporte la librería de mensajes ZMQ y pueda motar un socket SUB es factible de funcionar como cliente de Cardenal.

Para mas información revisa la sección `Clientes`

A continuación un ejemplo de como enviar mensajes con el cliente ``cardenal-python-client``::

    >> from CardenalClient.client import CardenalCliet
    >> cli = CardenalClient('localhost')  # Estoy ejecutado el servidor localmente
    >> user_id = 12345  # Id de usuario de telegram
    >> username = 'myUsername'  # Username de telegram
    >> cli.txt_msg('Mensaje utilizando mi user ID', user_id=user_id)
    >> cli.txt_msg('Mensaje utilizado mi username', username=username)

Voila!

.. only:: html

   .. figure:: _misc/ex_02.gif
      :width: 250pt
      :align: center


.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. _ZMQ: http://zeromq.org/
.. _cardenal-python-client: http://github.com
.. _BotFather: https://core.telegram.org/bots#6-botfather
.. _`ZMQ lenguage Bindings`: http://zeromq.org/bindings:_start

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
