import requests

class APIWrapper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.sessao = requests.Session()

    def fazer_login(self, dados_login):
        url_login = f"{self.base_url}/Authentication/Authenticate"
        resposta = self.sessao.post(url_login, json=dados_login, verify=False)

        if resposta.status_code == 200:
            print("Login bem-sucedido.")
        else:
            print(f"Falha no login. Código de status: {resposta.status_code}")

    def fazer_outra_requisicao(self, rota, dados=None):
        url = f"{self.base_url}/{rota}"
        resposta = self.sessao.post(url, json=dados, verify=False)

        if resposta.status_code == 200:
            print(f"Resposta da rota {rota}:")
            print(resposta.json())
        else:
            print(f"Falha na requisição. Código de status: {resposta.status_code}")

# URL da API
api_url = "http://librebooking.teste/Web/Services/"

# Dados a serem enviados no login
dados_login = {
    "username": "ifsc",
    "password": "ifsc@libre"
}

# Criando uma instância da classe APIWrapper
api_wrapper = APIWrapper(api_url)

# Fazendo login
api_wrapper.fazer_login(dados_login)

# Fazendo outra requisição em uma rota diferente
rota_destino = "outra-rota"
dados_requisicao = {
    "parametro1": "valor1",
    "parametro2": "valor2"
}

# api_wrapper.fazer_outra_requisicao(rota_destino, dados_requisicao)
