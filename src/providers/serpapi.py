import requests
import os
import logging
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

def buscar_voos_serpapi(origem="GRU", destino="JFK", dias_para_ida=30):
    """Busca voos na SerpApi com parâmetros dinâmicos e fallback automático."""

    data_ida = (datetime.now() + timedelta(days=dias_para_ida)).strftime("%Y-%m-%d")
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        log.error("❌ Erro: Variável SERPAPI_KEY não encontrada!")
        return []

    params = {
        "departure_id": origem,
        "arrival_id": destino,
        "outbound_date": data_ida,
        "currency": "BRL",
        "hl": "pt",
        "adults": 1,
        "type": 2,
        "api_key": api_key
    }

    engines = ["google_flights", "google_flights_json"]

    for engine in engines:
        params["engine"] = engine
        try:
            r = requests.get("https://serpapi.com/search", params=params, timeout=20)
            r.raise_for_status()
            dados = r.json()

            if "error" in dados:
                log.error(f"❌ Erro na SerpApi ({engine}): {dados.get('error')}")
                continue

            voos_encontrados = []
            resultados = dados.get("best_flights", [])

            for voo in resultados:
                preco = voo.get("price", 0)
                destino_final = voo.get("flights", [{}])[0].get("arrival_airport", {}).get("name", destino)
                voos_encontrados.append({
                    "origem": origem,
                    "destino": destino_final,
                    "preco": preco,
                    "data": data_ida,
                    "link": "https://www.google.com/flights",
                    "international": True
                })

            if voos_encontrados:
                log.info(f"📊 API ({engine}) retornou {len(voos_encontrados)} voos")
                return voos_encontrados

        except Exception as e:
            log.error(f"❌ ERRO CRÍTICO NA REQUISIÇÃO ({engine}): {e}")

    log.warning("⚠️ Nenhum voo encontrado em nenhum engine.")
    return []
