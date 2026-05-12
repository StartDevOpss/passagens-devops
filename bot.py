import os
import logging
import time
import requests
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

    if any(cidade in destino for cidade in ["miami", "paris", "lisboa", "new york", "orlando"]):
        return "internacional"
    elif any(cidade in destino for cidade in ["rio de janeiro", "santos dumont", "congonhas", "porto alegre"]):
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
            for oferta in ofertas_encontradas:
                grupo = classificar_grupo(oferta)
                log.info(f"✈️ Oferta encontrada ({grupo}): {oferta}")
                enviar_notificacao_discord(oferta, grupo=grupo)
        else:
            log.warning("⚠️ Nenhuma oferta encontrada.")

        log.info("⏳ Aguardando próxima execução...")
        time.sleep(3600)

if __name__ == "__main__":
    monitorar_voos()
