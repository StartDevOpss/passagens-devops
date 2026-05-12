import time
import logging
import json
import os
import requests
from config import AIRPORTS, INTERVALO_HORAS
from router import get_webhook_url
from providers.serpapi import buscar_voos_serpapi

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Caminhos ajustados para o volume do Kubernetes
CACHE_FILE = "docs/ofertas_vistas.json"
OFERTAS_FILE = "docs/ofertas.json"

def carregar_vistas():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def salvar_vista(oferta_id):
    vistas = carregar_vistas()
    if oferta_id not in vistas:
        vistas.append(oferta_id)
        with open(CACHE_FILE, "w") as f:
            json.dump(vistas, f)

def atualizar_dashboard(novas_ofertas):
    """Salva as ofertas no arquivo que o site Dark Mode lê"""
    with open(OFERTAS_FILE, "w") as f:
        json.dump(novas_ofertas, f, indent=4)

def iniciar_monitoramento():
    log.info("🚀 FlightHunter Iniciado - Monitorando BSB, SP, RJ e PR")
    
    while True:
        vistas = carregar_vistas()
        todas_ofertas_atuais = [] # Para o dashboard
        
        for regiao, aeroportos in AIRPORTS.items():
            for origem in aeroportos:
                log.info(f"🔎 Verificando voos saindo de: {origem} ({regiao})")
                
                ofertas_encontradas = buscar_voos_serpapi(origem)
                
                for oferta in ofertas_encontradas:
                    # PADRONIZAÇÃO: O router espera 'price' e 'destination'
                    # Se a SerpApi trouxer 'preco', nós criamos as chaves que o router quer
                    oferta['price'] = oferta.get('preco', oferta.get('price'))
                    oferta['destination'] = oferta.get('destino', oferta.get('destination'))
                    
                    todas_ofertas_atuais.append(oferta)
                    
                    # ID único para não repetir alerta
                    oferta_id = f"{oferta['destination']}-{oferta['price']}"
                    
                    if oferta_id not in vistas:
                        log.info(f"✨ Nova oferta encontrada: {oferta['destination']} por R$ {oferta['price']}")
                        
                        webhook_url = get_webhook_url(oferta)
                        if webhook_url:
                            enviar_para_discord(webhook_url, oferta)
                            salvar_vista(oferta_id)
                        else:
                            log.warning(f"⚠️ Nenhuma regra de roteamento serviu para {oferta['destination']}")
        
        # Atualiza o arquivo que o HTML lê
        atualizar_dashboard(todas_ofertas_atuais)
        
        log.info(f"⏰ Ciclo completo. Próxima busca em {INTERVALO_HORAS}h")
        time.sleep(INTERVALO_HORAS * 3600)

def enviar_para_discord(url, oferta):
    mensagem = {
        "content": f"🔥 **PROMOÇÃO ENCONTRADA**\n\n"
                   f"✈️ **Origem:** {oferta.get('origem')}\n"
                   f"📍 **Destino:** {oferta['destination']}\n"
                   f"💰 **Preço: R$ {oferta['price']}**\n"
                   f"📅 **Data:** {oferta.get('data', 'Consultar')}\n\n"
                   f"🔗 **Link:** {oferta.get('link', 'https://www.google.com/flights')}"
    }
    
    try:
        requests.post(url, json=mensagem, timeout=10)
        log.info(f"✅ Alerta enviado para o Discord: {oferta['destination']}")
    except Exception as e:
        log.error(f"❌ Falha ao enviar Webhook: {e}")

if __name__ == "__main__":
    iniciar_monitoramento()