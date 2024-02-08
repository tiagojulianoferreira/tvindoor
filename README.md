# TV Indoor
TV Indoor ou Painel para visualização de horário de aulas e localização de salas/professores

# Requisitos
- Debian/Ubuntu Linux
- Python3 com python3-pip e python3-venv
- Chromedriver

# Preparação
Instalei os pacotes Python necessários.
```shell
sudo apt install python3-pip python3-venv -y
```
Instale o chomedriver que será usado pelo Selenium
```shell
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb

google-chrome --version
```
# Instalação
Clone o repositório em uma pasta (ex: /opt/)
```shell
https://github.com/tiagojulianoferreira/tvindoor.git
```
Acesse o diretório e instale as dependências;
```shell
cd tvindoor/
pip3 install -r requirements
```
# Execução
Execute o servidor gunicor na porta e número de workers escolhidos.
```shell
cd /opt/tvindoor
source .venv/bin/active
gunicorn -w 8 --bind 0.0.0.0:5053 wsgi:app
```
## Features
    - Agenda de horários e salas consumindo API LibreBooking
    - Slider de avisos
    - Widget de temperatura e horário no rodapé

## TO DO
    - [ ] Consumir a rota Scheduler da API LibreBooking
    - [ ] Construir formulário gerador de conteúdo de avisos (Interface Adm)
    - [ ] Construir backend consumir OpenWeatherMap