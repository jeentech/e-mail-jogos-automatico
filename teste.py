import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --------- CONFIGS ---------
API_KEY = "b3785e9edbmsh1d6e379713f6284p175198jsne0a1c9ec1e3d"
HOJE = datetime.now(timezone.utc).strftime('%Y-%m-%d')
HOJE_BR = datetime.now().strftime('%d/%m')

remetente = "jeniioliveira23@gmail.com"
destinatarios = ["jeniioliveira23@gmail.com"]
senha_app = "xnnd hjax biny fzad"

# --------- FUNÇÃO: Buscar jogos dos clubes brasileiros ---------
def buscar_jogos_brasileiros():
    ligas_ids = {
        "Brasileirão Série A": 71,
        "Brasileirão Série B": 72,
        "Copa do Brasil": 73,
        "Libertadores": 13,
        "Sul-Americana": 14
    }

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    fuso_brasilia = pytz.timezone('America/Sao_Paulo')
    jogos_por_competicao = {}

    for nome_liga, id_liga in ligas_ids.items():
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        params = {"date": HOJE, "league": id_liga, "season": "2023"}
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code == 200:
            dados = resp.json().get('response', [])
            if not dados:
                continue
            jogos = []
            for jogo in dados:
                time_casa = jogo['teams']['home']['name']
                time_fora = jogo['teams']['away']['name']
                horario_utc = datetime.fromisoformat(jogo['fixture']['date'].replace("Z", "+00:00"))
                horario_brt = horario_utc.astimezone(fuso_brasilia)
                horario_str = horario_brt.strftime('%H:%M')
                jogos.append(f"<li><b>{time_casa} x {time_fora}</b> - {horario_str}</li>")
            jogos_por_competicao[nome_liga] = jogos
        else:
            print(f"Erro ao buscar {nome_liga}: {resp.status_code}")

    return jogos_por_competicao

# --------- FUNÇÃO: Buscar jogos do Mundial de Clubes via web ---------
def buscar_mundial_clubes():
    url = "https://ge.globo.com/futebol/mundial-de-clubes/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    jogos = []

    for link in soup.find_all('a'):
        txt = link.text.strip()
        if HOJE_BR in txt and ('x' in txt or 'X' in txt):
            jogos.append(f"<li>{txt}</li>")
    return jogos

# --------- MONTA CORPO DO E-MAIL ---------
corpo_email = f"<h2>📅 Jogos do Dia - {HOJE_BR}</h2>"

# Mundial de Clubes
jogos_mundial = buscar_mundial_clubes()
if jogos_mundial:
    corpo_email += "<h3>🏆 Copa do Mundo de Clubes:</h3><ul>"
    corpo_email += "".join(jogos_mundial)
    corpo_email += "</ul>"

# Clubes brasileiros em diversas competições
jogos_brasileiros = buscar_jogos_brasileiros()
if jogos_brasileiros:
    for liga, jogos in jogos_brasileiros.items():
        corpo_email += f"<h3>🇧🇷 {liga}:</h3><ul>"
        corpo_email += "".join(jogos)
        corpo_email += "</ul>"

if not jogos_mundial and not jogos_brasileiros:
    corpo_email += "<p>Não há jogos programados para hoje.</p>"

# --------- ENVIA E-MAIL ---------
msg = MIMEMultipart()
msg['From'] = remetente
msg['To'] = ", ".join(destinatarios)
msg['Subject'] = f"Jogos do dia - {HOJE_BR}"
msg.attach(MIMEText(corpo_email, 'html'))

try:
    with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
        servidor.starttls()
        servidor.login(remetente, senha_app)
        servidor.send_message(msg)
    print("✅ E-mail enviado com sucesso!")
except Exception as e:
    print("❌ Erro ao enviar e-mail:", e)
