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
    "geral": os.getenv("DISCORD_WEBHOOK_GERAL"),
    "internacional": os.getenv("DISCORD_WEBHOOK_INTERNACIONAL"),
    "brasil": os.getenv("DISCORD_WEBHOOK_BRASIL"),
    "voos_malucos": os.getenv("DISCORD_WEBHOOK_MALUCOS"),
    "datas_especificas": os.getenv("DISCORD_WEBHOOK_DATAS")
}

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "StartDevOpss/passagens-devops")
GITHUB_FILE_PATH = "docs/ofertas.json"

def salvar_e_publicar_ofertas(todas_ofertas):
    """Salva ofertas no GitHub Pages via API do GitHub."""
    if not GITHUB_TOKEN:
        log.warning("⚠️ GITHUB_TOKEN não configurado, pulando publicação.")
        return

    payload = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "total": len(todas_ofertas),
        "ofertas": todas_ofertas
    }

    conteudo = json.dumps(payload, ensure_ascii=False, indent=2)
    conteudo_b64 = __import__("base64").b64encode(conteudo.encode()).decode()

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Pega o SHA atual do arquivo (necessário para atualizar)
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
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

def enviar_notificacao_discord(oferta, grupo="geral"):
    webhook = DISCORD_WEBHOOKS.get(grupo)
    if not webhook:
        log.error(f"❌ Webhook não configurado para o grupo {grupo}")
        return

    mensagem = (
        f"✈️ Oferta encontrada!\n"
        f"Origem: {oferta['origem']}\n"
        f"Destino: {oferta['destino']}\n"
        f"Preço: R${oferta['preco']}\n"
        f"Data: {oferta['data']}\n"
        f"Link: {oferta['link']}"
    )

    try:
        r = requests.post(webhook, json={"content": mensagem}, timeout=10)
        r.raise_for_status()
        log.info(f"✅ Notificação enviada ao Discord ({grupo}).")
    except Exception as e:
        log.error(f"❌ Erro ao enviar notificação ao Discord ({grupo}): {e}")

def classificar_grupo(oferta):
    destino = oferta["destino"].lower()

    if any(c in destino for c in ["miami", "paris", "lisboa", "new york", "orlando"]):
        return "internacional"
    elif any(c in destino for c in ["rio de janeiro", "santos dumont", "congonhas", "porto alegre"]):
        return "brasil"
    elif oferta["preco"] < 500:
        return "voos_malucos"
    elif oferta["data"].endswith("-25"):
        return "datas_especificas"
    else:
        return "geral"

def monitorar_voos():
    while True:
        log.info("🔍 Iniciando busca de voos...")

        ofertas_encontradas = buscar_voos_serpapi(origem="GRU", destino="SDU", dias_para_ida=15)

        if ofertas_encontradas:
            todas_com_grupo = []
            for oferta in ofertas_encontradas:
                grupo = classificar_grupo(oferta)
                oferta["grupo"] = grupo
                log.info(f"✈️ Oferta encontrada ({grupo}): {oferta}")
                enviar_notificacao_discord(oferta, grupo=grupo)
                todas_com_grupo.append(oferta)

            # Publica no GitHub Pages
            salvar_e_publicar_ofertas(todas_com_grupo)
        else:
            log.warning("⚠️ Nenhuma oferta encontrada.")

        log.info("⏳ Aguardando próxima execução...")
        time.sleep(3600)

if __name__ == "__main__":
    monitorar_voos()