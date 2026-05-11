import requests
import schedule
import time
import json
import os
import logging
from config import (
    DISCORD_WEBHOOK_URL, ORIGEM, ADULTOS,
    PRECO_MIN, PRECO_MAX, DESTINOS, INTERVALO_HORAS
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)
log = logging.getLogger(__name__)

ARQUIVO_VISTAS  = "ofertas_vistas.json"
ARQUIVO_OFERTAS = "docs/ofertas.json"

# ── cole sua chave aqui ────────────────────────────────────────────────────────────────────────
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

os.makedirs("docs", exist_ok=True)

def carregar_vistas():
    if os.path.exists(ARQUIVO_VISTAS):
        with open(ARQUIVO_VISTAS) as f:
            return set(json.load(f))
    return set()

def salvar_vistas(vistas):
    with open(ARQUIVO_VISTAS, "w") as f:
        json.dump(list(vistas), f)

def carregar_ofertas():
    if os.path.exists(ARQUIVO_OFERTAS):
        with open(ARQUIVO_OFERTAS) as f:
            return json.load(f)
    return []

def salvar_ofertas(ofertas):
    with open(ARQUIVO_OFERTAS, "w", encoding="utf-8") as f:
        json.dump(ofertas, f, ensure_ascii=False, indent=2)

def enviar_discord(oferta):
    embed = {
        "embeds": [{
            "title": f"✈️ {oferta['origem']} → {oferta['destino']} | R$ {oferta['preco_total']:.0f} (2 pessoas)",
            "url": oferta["link"],
            "color": 3066993,
            "fields": [
                {"name": "💰 Por pessoa",  "value": f"R$ {oferta['preco_pessoa']:.0f}", "inline": True},
                {"name": "👥 Total (2px)", "value": f"R$ {oferta['preco_total']:.0f}",  "inline": True},
                {"name": "✈️ Cia aérea",   "value": oferta.get("cia", "N/A"),           "inline": True},
                {"name": "📅 Ida",         "value": oferta["data_ida"],                 "inline": True},
                {"name": "📅 Volta",       "value": oferta["data_volta"],               "inline": True},
                {"name": "⏱️ Duração",     "value": oferta.get("duracao", "N/A"),       "inline": True},
            ],
            "footer": {"text": "PassagensBot · Google Flights"},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }]
    }
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=embed, timeout=10)
        if r.status_code in (200, 204):
            log.info(f"  ✅ Discord: {oferta['origem']} → {oferta['destino']}")
        else:
            log.warning(f"  ❌ Discord {r.status_code}: {r.text[:100]}")
    except Exception as e:
        log.error(f"  ❌ Falha Discord: {e}")

def buscar_voos(destino):
    # datas: ida daqui 30 dias, volta daqui 37 dias
    data_ida   = time.strftime("%Y-%m-%d", time.localtime(time.time() + 30 * 86400))
    data_volta = time.strftime("%Y-%m-%d", time.localtime(time.time() + 37 * 86400))

    params = {
        "engine":          "google_flights",
        "departure_id":    ORIGEM,
        "arrival_id":      destino,
        "outbound_date":   data_ida,
        "return_date":     data_volta,
        "adults":          ADULTOS,
        "currency":        "BRL",
        "hl":              "pt",
        "type":            "1",   # 1 = ida e volta
        "api_key":         SERPAPI_KEY,
    }

    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        if r.status_code != 200:
            log.warning(f"  ⚠️ SerpAPI {r.status_code} para {destino}")
            return []

        dados = r.json()
        ofertas = []

        # pega os voos da melhor opção e outras opções
        todos_voos = []
        if "best_flights" in dados:
            todos_voos += dados["best_flights"]
        if "other_flights" in dados:
            todos_voos += dados["other_flights"]

        for voo in todos_voos:
            preco_total  = voo.get("price", 0)
            preco_pessoa = preco_total / ADULTOS

            if not (PRECO_MIN <= preco_pessoa <= PRECO_MAX):
                continue

            # duração
            dur_min = voo.get("total_duration", 0)
            duracao = f"{dur_min // 60}h{dur_min % 60:02d}min" if dur_min else "N/A"

            # cia aérea
            flights = voo.get("flights", [])
            cias = ", ".join(set(
                f.get("airline", "") for f in flights if f.get("airline")
            )) or "N/A"

            # datas reais
            d_ida   = flights[0].get("departure_airport", {}).get("time", data_ida)[:10] if flights else data_ida
            d_volta = flights[-1].get("arrival_airport", {}).get("time", data_volta)[:10] if flights else data_volta

            # link direto para o Google Flights
            link = (
                f"https://www.google.com/travel/flights?"
                f"hl=pt&curr=BRL"
            )

            ofertas.append({
                "id":            f"{ORIGEM}-{destino}-{preco_total}-{d_ida}",
                "origem":        ORIGEM,
                "destino":       destino,
                "preco_pessoa":  round(preco_pessoa, 2),
                "preco_total":   round(preco_total, 2),
                "data_ida":      d_ida,
                "data_volta":    d_volta,
                "link":          link,
                "cia":           cias,
                "duracao":       duracao,
                "encontrada_em": time.strftime("%d/%m/%Y %H:%M"),
            })

        return ofertas

    except Exception as e:
        log.error(f"  ⚠️ Erro {destino}: {e}")
        return []

def buscar_passagens():
    vistas         = carregar_vistas()
    todas_ofertas  = carregar_ofertas()
    ids_existentes = {o["id"] for o in todas_ofertas}
    total_novo     = 0

    log.info(f"✈️  Buscando | {ORIGEM} | {ADULTOS}pax | R${PRECO_MIN}–R${PRECO_MAX}/pessoa")

    for destino in DESTINOS:
        log.info(f"  📡 {ORIGEM} → {destino}")
        ofertas = buscar_voos(destino)
        log.info(f"     {len(ofertas)} oferta(s) na faixa")

        for oferta in ofertas:
            oid = oferta["id"]
            if oid in vistas:
                continue
            vistas.add(oid)
            total_novo += 1
            if oid not in ids_existentes:
                todas_ofertas.append(oferta)
                ids_existentes.add(oid)
            enviar_discord(oferta)
            time.sleep(2)

        time.sleep(3)

    todas_ofertas = sorted(todas_ofertas, key=lambda x: x["preco_total"])[:200]
    salvar_ofertas(todas_ofertas)
    salvar_vistas(vistas)
    log.info(f"✅ Concluído — {total_novo} nova(s).")

if __name__ == "__main__":
    log.info("🚀 PassagensBot iniciado!")
    buscar_passagens()
    schedule.every(INTERVALO_HORAS).hours.do(buscar_passagens)
    log.info(f"⏰ Rodando a cada {INTERVALO_HORAS}h.")
    while True:
        schedule.run_pending()
        time.sleep(60)