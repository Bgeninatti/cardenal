echo "Creando carpetas"
mkdir log
echo "Instalando dependencias"
sudo apt-get install supervisor python3-venv
pyvenv-3.4 cardenal-venv
echo "Configurando supervisor..."
sudo cp config/cardenal-supervisor.conf /etc/supervisor/conf.d/cardenal.conf
