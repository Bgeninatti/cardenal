from setuptools import setup

setup(
    name='Cardenal',
    version='0.3.0',
    description='Cardenal is a TCP server (uses the library ZMQ) that ' +
                'recives text messages (in an early future images too!) and' +
                ' forward them to a certain clients that have made ' +
                'suscription to a Telegram bot.',
    author='Bruno Geninatti',
    author_email='brunogeninatti@gmail.com',
    packages=['Cardenal'],
    test_suite='tests',
    install_requires=['pyzmq', 'peewee', 'python-telegram-bot'],
)
