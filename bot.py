import os
import json
import logging
import time
import requests
from datetime import datetime
from src.providers.serpapi import buscar_voos_serpapi

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

DISCORD_WEBHOOKS = {
    "geral":             os.getenv("DISCORD_WEBHOOK_GERAL"),
    "internacional":     os.getenv("DISCORD_WEBHOOK_INTERNACIONAL"),
    "brasil":            os.getenv("DISCORD_WEBHOOK_BRASIL"),
    "voos_malucos":      os.getenv("DISCORD_WEBHOOK_MALUCOS"),
    "datas_especificas": os.getenv("DISCORD_WEBHOOK_DATAS")
}

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO  = os.getenv("GITHUB_REPO", "StartDevOpss/passagens-devops")
GITHUB_FILE  = "docs/ofertas.json"   # ← CORRIGIDO: pasta que o GitHub Pages serve

PRECO_MAXIMO_BRASIL         = 1500
PRECO_MAXIMO_INTERNACIONAL  = 5000

ROTAS = [
    # Brasil
    {"origem": "GRU", "destino": "SDU", "dias": 15},
    {"origem": "GRU", "destino": "POA", "dias": 15},
    {"origem": "GRU", "destino": "CWB", "dias": 15},
    {"origem": "GRU", "destino": "SSA", "dias": 15},
    {"origem": "GRU", "destino": "REC", "dias": 15},
    # Internacional
    {"origem": "GRU", "destino": "MIA", "dias": 30},
    {"origem": "GRU", "destino": "LIS", "dias": 30},
    {"origem": "GRU", "destino": "CDG", "dias": 30},
    {"origem": "GRU", "destino": "MAD", "dias": 30},
    {"origem": "GRU", "destino": "JFK", "dias": 30},
]

DESTINOS_INTERNACIONAIS = [
    "miami", "paris", "lisboa", "new york", "orlando",
    "madrid", "roma", "tóquio", "tokyo", "bangkok",
    "london", "londres", "dubai", "cancun", "bogotá",
    "john f", "charles de gaulle", "heathrow"
]

DESTINOS_BRASIL = [
    "rio de janeiro", "santos dumont", "congonhas",
    "porto alegre", "salvador", "recife", "fortaleza",
    "curitiba", "brasília", "manaus", "belém", "salgado filho",
    "afonso pena", "deputado luis eduardo"
]

def classificar_grupo(oferta):
    destino = oferta["destino"].lower()
    preco   = oferta["preco"]
    data    = oferta["data"]

    if any(d in destino for d in DESTINOS_INTERNACIONAIS):
        if preco > 0 and preco < 1500:
            return "voos_malucos"
        return "internacional"
    elif any(d in destino for d in DESTINOS_BRASIL):
        if preco > 0 and preco < 400:
            return "voos_malucos"
        return "brasil"
    elif data.endswith("-25") or data.endswith("-01"):
        return "datas_especificas"
    else:
        return "geral"

def enviar_notificacao_discord(oferta, grupo="geral"):
    webhook = DISCORD_WEBHOOKS.get(grupo)
    if not webhook:
        log.error(f"❌ Webhook não configurado para o grupo {grupo}")
        return

    emoji = {
        "brasil":            "🇧🇷",
        "internacional":     "🌍",
        "voos_malucos":      "🤪",
        "datas_especificas": "📅",
        "geral":             "✈️"
    }.get(grupo, "✈️")

    preco_str    = f"R$ {oferta['preco']}" if oferta['preco'] > 0 else "Consulte o preço"
    companhia    = oferta.get("companhia") or "N/D"
    duracao      = oferta.get("duracao") or "N/D"
    partida      = oferta.get("partida") or "N/D"
    paradas      = oferta.get("paradas", 0)
    paradas_str  = "✅ Direto" if paradas == 0 else f"{paradas} escala(s)"

    mensagem = (
        f"{emoji} **Oferta de Passagem!**\n"
        f"✈️ **{oferta['origem']} → {oferta['destino']}**\n"
        f"💰 Preço: **{preco_str}**\n"
        f"📅 Data: {oferta['data']} às {partida}\n"
        f"⏱️ Duração: {duracao} | {paradas_str}\n"
        f"🏢 Companhia: {companhia}\n"
        f"🔗 {oferta['link']}"
    )

    try:
        r = requests.post(webhook, json={"content": mensagem}, timeout=10)
        r.raise_for_status()
        log.info(f"✅ Notificação enviada ao Discord ({grupo}).")
    except Exception as e:
        log.error(f"❌ Erro ao enviar notificação ({grupo}): {e}")

def salvar_e_publicar_ofertas(todas_ofertas):
    if not GITHUB_TOKEN:
        log.warning("⚠️ GITHUB_TOKEN não configurado, pulando publicação.")
        return

    payload = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "total": len(todas_ofertas),
        "ofertas": todas_ofertas
    }

    conteudo     = json.dumps(payload, ensure_ascii=False, indent=2)
    conteudo_b64 = __import__("base64").b64encode(conteudo.encode()).decode()
    headers      = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    sha = None
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            sha = r.json()["sha"]
    except Exception:
        pass

    body = {
        "message": f"chore: atualiza ofertas {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": conteudo_b64,
        "branch": "main"
    }
    if sha:
        body["sha"] = sha

    try:
        r = requests.put(url, headers=headers, json=body, timeout=10)
        r.raise_for_status()
        log.info("✅ ofertas.json publicado no GitHub Pages.")
    except Exception as e:
        log.error(f"❌ Erro ao publicar no GitHub: {e}")

def monitorar_voos():
    while True:
        log.info("🔍 Iniciando busca de voos...")
        todas_ofertas = []

        for rota in ROTAS:
            ofertas = buscar_voos_serpapi(
                origem=rota["origem"],
                destino=rota["destino"],
                dias_para_ida=rota["dias"]
            )

            for oferta in ofertas:
                grupo = classificar_grupo(oferta)

                oferta["grupo"] = grupo
                todas_ofertas.append(oferta)

                if oferta["preco"] == 0:
                    continue

                limite = PRECO_MAXIMO_INTERNACIONAL if grupo == "internacional" else PRECO_MAXIMO_BRASIL
                if oferta["preco"] > limite:
                    log.info(f"⏭️ Ignorado (preço alto R${oferta['preco']}): {oferta['destino']}")
                    continue

                enviar_notificacao_discord(oferta, grupo=grupo)
                time.sleep(1)

            time.sleep(2)

        if todas_ofertas:
            salvar_e_publicar_ofertas(todas_ofertas)
        else:
            log.warning("⚠️ Nenhuma oferta encontrada.")

        log.info(f"⏳ Aguardando próxima execução... ({len(todas_ofertas)} ofertas encontradas)")
        time.sleep(3600)

if __name__ == "__main__":
    monitorar_voos()