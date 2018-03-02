# Cardenal

## First advice

If you are a person that have to run time demanding process or tests in some project and feel the need to notify events or logs easily to your cellphone, then you are in the right place.

If you don't but still feel courious about what Cardenal is... ok, just keep reading.

## What it does?

Cardenal is a TCP server (uses the library [ZMQ](http://zeromq.org/)) that recives text messages (in an early future images too!) and forward them to a certain clients that have made suscription to a Telegram bot.

The server is coded entearly in python, but the clients could be for any language that supports ZMQ. A good start to know the alcance is check the [ZMQ lenguage Bindings](http://zeromq.org/bindings:_start)

The first client was for python too and is the one that we use in this documentation for our examples. You can check the project in te GitHub repository here: [cardenal-python-client](https://github.com/Bgeninatti/cardenal-python-client)

## Documentation

Here's the docs: http://cardenal.readthedocs.io/en/latest/
