DIR="cardenal"

echo "Creando carpetas"
mkdir $DIR
mkdir $DIR"/log"
echo "Instalando dependencias"
sudo apt-get install supervisor python3-venv
pyvenv $DIR"/venv"
source $DIR"/venv/bin/activate"
pip3 install -r requirements.txt
cp cardenal.py models.py zmq_server.py $DIR
#echo "Configurando supervisor..."
#sudo cp config/cardenal-supervisor.conf /etc/supervisor/conf.d/cardenal.conf
