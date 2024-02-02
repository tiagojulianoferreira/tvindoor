import os
from flask import Flask, render_template, jsonify, send_from_directory, json
import requests, datetime
from pytz import timezone
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Isso permite todas as origens

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class APIWrapper:
    def __init__(self, openweathermap_api_key):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.openweathermap_api_key = openweathermap_api_key

    def get_weather_data(self, city):
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': self.openweathermap_api_key,
            'units': 'metric'
        }

        response = requests.get(weather_url, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        else:
            return None

# Chave da API do OpenWeatherMap
# owm_api_key = "8ca3161edf12585a048cc2f0d2433493"
owm_api_key = os.getenv("OWM_KEY")

# Criando uma instância da classe APIWrapper
api_wrapper = APIWrapper(owm_api_key)

# Carregar os dados do arquivo JSON
with open('reservas.json', 'r', encoding='utf-8') as f:
    reservas = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', reservas=reservas)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/data')
def get_data():
    return jsonify(reservas)

@app.route('/api/owm')
def get_owm_data():
    # Obter dados de temperatura, horário e previsão do tempo para a cidade desejada (por exemplo, "London")
    weather_data = api_wrapper.get_weather_data("Tubarão")

    # Obter a descrição do estado do tempo a partir dos dados da API
    weather_description = weather_data.get('weather', [{}])[0].get('description', '')

    # Traduzir para o português (exemplo simples)
    translation_dict = {
                'clear sky': {'translation': 'céu limpo', 'icon': 'wi-day-sunny'},
                'few clouds': {'translation': 'poucas nuvens', 'icon': 'wi-day-sunny-overcast'},
                'scattered clouds': {'translation': 'nuvens dispersas', 'icon': 'url_do_icone_nuvens_dispersas'},
                'rain': {'translation': 'chuva', 'icon': 'wi-day-rain'},
                'thunderstorm': {'translation': 'tempestade', 'icon': 'wi-day-thunderstorm'},
                
            }
               
    translated_forecast = translation_dict.get(weather_description.lower(), weather_description)

    # Obter o horário da última atualização e formatar para o padrão brasileiro
    last_update_timestamp = weather_data.get('dt', 0)
    last_update_time = datetime.datetime.utcfromtimestamp(last_update_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    # Ajustar o horário para o fuso horário brasileiro
    last_update_time_brazilian = datetime.datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone('UTC')).astimezone(timezone('America/Sao_Paulo')).strftime('%H:%M')

    # Obter o horário atual em tempo real
    horario_atual = datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M')
   
    # Processar weather_data conforme necessário
    temperature = weather_data.get('main', {}).get('temp')
    time = horario_atual
    forecast = translated_forecast  

    data = {
        'temperature': round(temperature,0),
        'time': horario_atual,
        'forecast': forecast,
    }

    return jsonify(data)
@app.route('/api/scrapy')
def get_reservations():
    # URL da página de login
    login_url = os.getenv("BOOKED_LOGIN_URL")

    # Dados de login obtidos do arquivo .env
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    # Verificar se as variáveis de e-mail e senha foram carregadas corretamente
    if email is None or password is None:
        raise ValueError("As variáveis de e-mail e senha não foram encontradas no arquivo .env")
    # Dados de login
    login_payload = {
        'email': email,
        'password': password
    }

    # URL do dashboard após o login
    dashboard_url = os.getenv('BOOKED_DASHBOARD_URL')

    # Configurações para usar o navegador Chrome
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')  # Execute em segundo plano, remova se desejar visualização
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(login_url)

    # Preencher o formulário de login
    username_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys(login_payload['email'])
    password_field.send_keys(login_payload['password'])
    password_field.send_keys(Keys.RETURN)
    # Aguardar um tempo suficiente para o login ser processado (ajuste conforme necessário)
    time.sleep(5)
    # Verificar se o redirecionamento ocorreu
    if driver.current_url == dashboard_url:
        # Página do dashboard após o login bem-sucedido

        # Usando BeautifulSoup para analisar a página
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Encontra todas as reservas
        reservations = soup.find_all('div', class_='reservation')

        # Lista para armazenar as informações extraídas
        results = []
        # Itera sobre cada reserva e extrai as informações desejadas
        for reservation in reservations:
            # Extrai o horário
            horario = reservation.find('div', class_='col-sm-2 col-xs-6').text.strip()
            # Extrai o título
            titulo = reservation.find('div', class_='col-sm-4 col-xs-12').text.strip()
            # Extrai o local
            local_div = reservation.find('div', class_='col-sm-3 col-xs-12')
            local = local_div.text.strip()
            # Extrai o responsável
            responsavel = local_div.find_next_sibling('div').text.strip()
            # Adiciona as informações ao dicionário
            reservation_info = {
                "Horário": horario,
                "Título": titulo,
                "Local": local,
                "Responsável": responsavel
            }
            # Adiciona o dicionário à lista de resultados
            results.append(reservation_info)

        # Salvar os resultados em um arquivo JSON
        with open('reservas.json', 'w', encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=2)

        print("Resultados salvos em 'reservas.json'.")

    else:
        print("O login falhou. Verifique as credenciais ou a lógica de redirecionamento.")

    # Fechar o navegador após a conclusão
    driver.quit()

if __name__ == '__main__':
    get_reservations()
    
    app.run(debug=True, host='0.0.0.0', port=5053)
