import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Carregar as variáveis do .env
load_dotenv()

# Carregar o token e ID do chat das variáveis de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# URL do processo
url = "https://tjrj.pje.jus.br/1g/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam?ca=ca1b3c7702f5862c51fe6aa8050a15730e9d070b0ec03ec6"

# Cabeçalho do navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
}

# Data da última movimentação registrada
ultima_data_registrada = datetime.strptime("24/07/2024 09:38:38", "%d/%m/%Y %H:%M:%S")

def verificar_movimentacoes():
    # Fazendo a requisição HTTP
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao acessar o site. Código de status: {response.status_code}")
        return

    # Parsing do conteúdo HTML
    soup = BeautifulSoup(response.content, "html.parser")
    texto_completo = soup.get_text()

    # Procurando todas as movimentações no texto completo usando regex
    regex_movimentacao = r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) - (.+)"
    movimentacoes_encontradas = re.findall(regex_movimentacao, texto_completo)

    novas_movimentacoes = []

    for data_texto, descricao in movimentacoes_encontradas:
        # Converte a data para objeto datetime
        data_movimentacao = datetime.strptime(data_texto, "%d/%m/%Y %H:%M:%S")
        
        # Verifica se a data é posterior à última registrada
        if data_movimentacao > ultima_data_registrada:
            novas_movimentacoes.append((data_texto, descricao))

    # Se houver novas movimentações, envia notificação para o Telegram
    if novas_movimentacoes:
        mensagem = "Novas movimentações encontradas:\n"
        for data, desc in novas_movimentacoes:
            mensagem += f"{data} - {desc}\n"
        enviar_telegram(mensagem)
    else:
        print("Nenhuma movimentação nova encontrada.")

def enviar_telegram(mensagem, bot_token=TELEGRAM_BOT_TOKEN, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Falha ao enviar mensagem. Código de status: {response.status_code}")

# Executa a verificação
verificar_movimentacoes()