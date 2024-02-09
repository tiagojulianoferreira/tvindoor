import os
import datetime
import time
import threading
from flask import Flask, render_template, jsonify, send_from_directory, json, current_app
from pytz import timezone
from flask_cors import CORS
import schedule
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from backend.owm import APIWrapper

app = Flask(__name__)
CORS(app)  # Isso permite todas as origens

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Chave da API do OpenWeatherMap
owm_api_key = os.getenv("OWM_KEY")

# Criando uma instância da classe APIWrapper
api_wrapper = APIWrapper(owm_api_key)

# Definir um lock para sincronização entre get_reservations e get_data
reservation_lock = threading.Lock()

# Variável para armazenar as reservas
reservas = []

# URL da página de login e dados de login
login_url = os.getenv("BOOKED_LOGIN_URL")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

# URL do dashboard após o login
dashboard_url = os.getenv('BOOKED_DASHBOARD_URL')

# Função para fazer login e obter as reservas
def get_reservations():
    global reservation_lock
    global reservas

    with app.app_context():
        # Dados de login
        payload = {
            "email": email,
            "password": password,
            "login": "submit"  # Este valor pode variar dependendo do formulário
        }

        # Adquira o bloqueio antes de acessar reservas
        reservation_lock.acquire()
        try:
            session = requests.Session()
            response = session.post(login_url, data=payload)

            if response.ok:
                # Verificar se o login foi bem-sucedido
                if response.url == dashboard_url:
                    print("Login bem-sucedido. Redirecionado para o painel.")
                    # Página do dashboard após o login bem-sucedido
                    soup = BeautifulSoup(response.text, 'html.parser')
                    reservations = soup.find_all('div', class_='reservation')

                    results = []
                    for reservation in reservations:
                        horario = reservation.find('div', class_='col-sm-2 col-xs-6').text.strip()
                        titulo = reservation.find('div', class_='col-sm-4 col-xs-12').text.strip()
                        local = reservation.find('div', class_='col-sm-3 col-xs-12').text.strip()
                        responsavel = reservation.find('div', class_='col-sm-3 col-xs-12').find_next_sibling('div').text.strip()

                        reservation_info = {
                            "Horário": horario,
                            "Título": titulo,
                            "Local": local,
                            "Responsável": responsavel
                        }
                        results.append(reservation_info)

                    # Atualizar a variável reservas após a obtenção das novas reservas
                    reservas = results
                    print(results)

                    # Salvar os resultados em um arquivo JSON
                    with open('reservas.json', 'w', encoding='utf-8') as json_file:
                        json.dump(results, json_file, ensure_ascii=False, indent=2)

                    print("Resultados salvos em 'reservas.json'.")
                else:
                    print("O login foi bem-sucedido, mas a página de destino é inesperada:", response.url)
            else:
                print("O login falhou. Verifique as credenciais.")
        finally:
            # Libere o bloqueio após a conclusão
            reservation_lock.release()

# Função para obter dados do OpenWeatherMap
def get_owm_data():
    with app.app_context():
        response = api_wrapper.get_weather_data(os.getenv("OWM_CITY"))

        if response.get('cod') == 200:
            weather_description = response.get('weather', [{}])[0].get('description', '')

            translation_dict = {
                'clear sky': {'translation': 'céu limpo', 'icon': 'wi-day-sunny'},
                'few clouds': {'translation': 'poucas nuvens', 'icon': 'wi-day-sunny-overcast'},
                'scattered clouds': {'translation': 'nuvens dispersas', 'icon': 'wi-day-sunny-overcast'},
                'rain': {'translation': 'chuva', 'icon': 'wi-day-rain'},
                'thunderstorm': {'translation': 'tempestade', 'icon': 'wi-day-thunderstorm'},
                'overcast clouds': {'translation': 'nublado', 'icon': 'wi-day-sunny-overcast'},
                'broken clouds': {'translation': 'nublado', 'icon': 'wi-cloudy'}
            }
            translated_forecast = translation_dict.get(weather_description.lower(), weather_description)

            last_update_timestamp = response.get('dt', 0)
            last_update_time = datetime.datetime.utcfromtimestamp(last_update_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
            last_update_time_brazilian = datetime.datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S UTC').replace(
                tzinfo=timezone('UTC')).astimezone(timezone('America/Sao_Paulo')).strftime('%H:%M')
            horario_atual = datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M')

            temperature = response.get('main', {}).get('temp')
            forecast = translated_forecast
            data = {
                'temperature': round(temperature, 0),
                'time': horario_atual,
                'forecast': forecast,
            }
            return jsonify(data)
        else:
            print("Erro ao obter dados do OpenWeatherMap:", response.get('message'))
            return jsonify({"error": "Erro ao obter dados do OpenWeatherMap"})

# Rota para exibir os dados
@app.route('/')
def index():
    global reservas
    return render_template('index.html', reservas=reservas)

# Rota para fornecer os dados das reservas
@app.route('/api/data')
def get_data():
    global reservas
    return jsonify(reservas)

# Rota para fornecer os dados do OpenWeatherMap
@app.route('/api/owm')
def get_owm_weather():
    return get_owm_data()

# Função para agendar tarefas
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Agendar a função get_reservations para ser executada a cada 5 minutos
schedule.every(1).minutes.do(get_reservations)

# Agendar a função get_owm_data para ser executada a cada 5 minutos
schedule.every(1).minutes.do(get_owm_data)

# Iniciar uma thread para executar o agendador de tarefas
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.daemon = True
schedule_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5053, use_reloader=True)
