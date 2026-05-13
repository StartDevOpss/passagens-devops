import requests
import os
import logging
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

def montar_link_google_flights(origem, destino, data_ida):
    """Monta link direto no Kayak com rota e data preenchidas."""
    return (
        f"https://www.kayak.com.br/flights/"
        f"{origem}-{destino}/{data_ida}?sort=price_a"
    )

def buscar_voos_serpapi(origem="GRU", destino="JFK", dias_para_ida=30):
    """Busca voos na SerpApi com parâmetros dinâmicos e fallback automático."""

    data_ida = (datetime.now() + timedelta(days=dias_para_ida)).strftime("%Y-%m-%d")
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        log.error("❌ Erro: Variável SERPAPI_KEY não encontrada!")
        return []

    params = {
        "engine": "google_flights",
        "departure_id": origem,
        "arrival_id": destino,
        "outbound_date": data_ida,
        "currency": "BRL",
        "hl": "pt",
        "adults": 1,
        "type": 2,
        "api_key": api_key
    }

    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        r.raise_for_status()
        dados = r.json()

        if "error" in dados:
            log.error(f"❌ Erro na SerpApi: {dados.get('error')}")
            return []

        voos_encontrados = []
        resultados = dados.get("best_flights", []) + dados.get("other_flights", [])

        for voo in resultados:
            preco = voo.get("price", 0)
            flights = voo.get("flights", [{}])
            destino_final = flights[0].get("arrival_airport", {}).get("name", destino)
            destino_iata = flights[-1].get("arrival_airport", {}).get("id", destino)

            voos_encontrados.append({
                "origem": origem,
                "destino": destino_final,
                "preco": preco,
                "data": data_ida,
                "link": montar_link_google_flights(origem, destino_iata, data_ida),
                "international": True
            })

        if voos_encontrados:
            log.info(f"📊 {len(voos_encontrados)} voos encontrados: {origem} → {destino}")

        return voos_encontrados

    except Exception as e:
        log.error(f"❌ ERRO CRÍTICO NA REQUISIÇÃO: {e}")
        return []