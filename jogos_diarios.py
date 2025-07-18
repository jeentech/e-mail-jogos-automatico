import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# --------- CONFIG ---------
API_KEY = "b3785e9edbmsh1d6e379713f6284p175198jsne0a1c9ec1e3d"

HOJE = datetime.now(timezone.utc).strftime('%Y-%m-%d')
HOJE_BR = datetime.now().strftime('%d/%m')
ANO_ATUAL = datetime.now().year

remetente = "jeentech.alerts@gmail.com"
destinatarios = [
    "jeniioliveira23@gmail.com", "Bellamorgon@gmail.com"
]
senha_app = "wlry qgop sqvi bxgy"

# --------- LIGAS ---------
ligas_ids = {
    "🇧🇷 Brasileirão Série A": 71,
    "🇧🇷 Brasileirão Série B": 72,
    "🇧🇷 Copa do Brasil": 73,
    "🇧🇷 Libertadores": 13,
    "🇧🇷 Sul-Americana": 14,
}

# --------- CLUBES INDIVIDUAIS ---------
clubes_brasileiros = {
    "Fluminense": 128,
    "Flamengo": 127,
    "Palmeiras": 126,
    "São Paulo": 135,
    "Corinthians": 131,
    "Internacional": 136,
    "Grêmio": 137,
    "Cruzeiro": 138,
    "Botafogo": 130,
    "Vasco": 139
}

# --------- FUNÇÃO: Buscar jogos por liga ---------
def buscar_jogos_ligas():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    fuso_brasilia = pytz.timezone('America/Sao_Paulo')
    jogos_por_liga = {}

    for nome_liga, id_liga in ligas_ids.items():
        try:
            resp = requests.get(
                "https://api-football-v1.p.rapidapi.com/v3/fixtures",
                headers=headers,
                params={"date": HOJE, "league": id_liga, "season": ANO_ATUAL},
                timeout=10
            )
            resp.raise_for_status()
            dados = resp.json().get('response', [])
        except Exception as e:
            print(f"⚠️ Falha ao buscar {nome_liga}: {e}")
            continue

        if dados:
            jogos = []
            for jogo in dados:
                casa = jogo['teams']['home']['name']
                fora = jogo['teams']['away']['name']
                utc = datetime.fromisoformat(jogo['fixture']['date'].replace("Z", "+00:00"))
                brt = utc.astimezone(fuso_brasilia).strftime('%H:%M')
                jogos.append(f"<li><b>{casa} x {fora}</b> - {brt}</li>")
            jogos_por_liga[nome_liga] = jogos

    return jogos_por_liga

# --------- FUNÇÃO: Buscar jogos por time ou seleção ---------
def buscar_jogos_time_especifico(time_id, nome_time):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    fuso_brasilia = pytz.timezone('America/Sao_Paulo')
    try:
        resp = requests.get(
            "https://api-football-v1.p.rapidapi.com/v3/fixtures",
            headers=headers,
            params={"date": HOJE, "team": time_id, "season": ANO_ATUAL},
            timeout=10
        )
        resp.raise_for_status()
        dados = resp.json().get('response', [])
    except Exception as e:
        print(f"⚠️ Erro ao buscar {nome_time}: {e}")
        return []

    jogos = []
    for jogo in dados:
        time_casa = jogo['teams']['home']['name']
        time_fora = jogo['teams']['away']['name']
        if nome_time.lower() not in time_casa.lower() and nome_time.lower() not in time_fora.lower():
            continue  # Ignora jogos que não envolvem esse time no nome
        utc = datetime.fromisoformat(jogo['fixture']['date'].replace("Z", "+00:00"))
        brt = utc.astimezone(fuso_brasilia).strftime('%H:%M')
        jogos.append(f"<li><b>{time_casa} x {time_fora}</b> - {brt}</li>")
    return jogos

# --------- FUNÇÃO: Scraper Globo (backup Mundial) ---------
def buscar_mundial_clubes():
    try:
        resp = requests.get("https://ge.globo.com/futebol/mundial-de-clubes/", timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        jogos = [
            f"<li>{link.text.strip()}</li>"
            for link in soup.find_all('a')
            if HOJE_BR in link.text and ('x' in link.text or 'X' in link.text)
        ]
        return jogos
    except Exception as e:
        print(f"⚠️ Não foi possível carregar Mundial de Clubes (pula): {e}")
        return []

# --------- MONTAR CORPO DO E-MAIL ---------
corpo = f"<h2>📅 Jogos do dia - {HOJE_BR}</h2>"

# Scraper Globo
mundial_scrap = buscar_mundial_clubes()
if mundial_scrap:
    corpo += "<h3>🌍 Jogos detectados pelo Globo:</h3><ul>" + "".join(mundial_scrap) + "</ul>"

# Ligas
jogos_ligas = buscar_jogos_ligas()
for liga, lista in jogos_ligas.items():
    corpo += f"<h3>{liga}:</h3><ul>" + "".join(lista) + "</ul>"

# Seleções
selecao_masc = buscar_jogos_time_especifico(1599, "Brasil")
if selecao_masc:
    corpo += "<h3>🇧🇷 Seleção Brasileira Masculina:</h3><ul>" + "".join(selecao_masc) + "</ul>"

selecao_fem = buscar_jogos_time_especifico(1598, "Brasil")
if selecao_fem:
    corpo += "<h3>🇧🇷 Seleção Brasileira Feminina:</h3><ul>" + "".join(selecao_fem) + "</ul>"

# Clubes brasileiros
for nome_time, time_id in clubes_brasileiros.items():
    jogos = buscar_jogos_time_especifico(time_id, nome_time)
    if jogos:
        corpo += f"<h3>🔷 Jogo do {nome_time}:</h3><ul>" + "".join(jogos) + "</ul>"

# Nenhum jogo encontrado
if not mundial_scrap and not jogos_ligas and not selecao_masc and not selecao_fem:
    corpo += "<p>❌ Nenhum jogo encontrado para hoje.</p>"

# --------- ENVIO DE E-MAIL ---------
msg = MIMEMultipart()
msg['From'] = remetente
msg['To'] = ", ".join(destinatarios)
msg['Subject'] = f"⚽ Jogos do dia - {HOJE_BR}"
msg.attach(MIMEText(corpo, 'html'))

def enviar_email():
    try:
        print("🚀 Iniciando envio de e-mail...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remetente, senha_app)
            server.send_message(msg)
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no envio de e-mail: {e}")
        print("⏳ Aguardando 60 segundos para tentar novamente...")
        time.sleep(60)
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(remetente, senha_app)
                server.send_message(msg)
            print("✅ E-mail enviado com sucesso na segunda tentativa!")
        except Exception as e2:
            print(f"❌ Segunda tentativa falhou também: {e2}")

enviar_email()
