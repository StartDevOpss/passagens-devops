import time
import logging
from config import AIRPORTS, INTERVALO_HORAS
from router import get_webhook_url
from providers.serpapi import buscar_voos_serpapi

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def iniciar_monitoramento():
    log.info("🚀 FlightHunter Iniciado - Monitorando BSB, SP, RJ e PR")
    
    while True:
        # Percorre cada região (SP, RJ, PR, BSB)
        for regiao, aeroportos in AIRPORTS.items():
            for origem in aeroportos:
                log.info(f"🔎 Verificando voos saindo de: {origem} ({regiao})")
                
                # Busca voos usando o provedor SerpAPI
                ofertas = buscar_voos_serpapi(origem)
                
                for oferta in ofertas:
                    # O router decide qual webhook usar
                    webhook_url = get_webhook_url(oferta)
                    
                    if webhook_url:
                        enviar_para_discord(webhook_url, oferta)
        
        log.info(f"⏰ Ciclo completo. Próxima busca em {INTERVALO_HORAS}h")
        time.sleep(INTERVALO_HORAS * 3600)

def enviar_para_discord(url, oferta):
    import requests
    # Aqui você mantém a lógica de embed que já tinha no seu bot.py antigo
    requests.post(url, json={"content": f"✈️ Nova oferta de {oferta['origem']}: R$ {oferta['preco']}"})

if __name__ == "__main__":
    iniciar_monitoramento()