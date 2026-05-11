import os

# ── discord ───────────────────────────────────────────────────
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1503195521848836127/535nqvQk5N2Pw_xBqYUHFBg9NFZ8M5BllFA2HK_Zd8yRnXcSo5MdKlEGE5AB_MZAFMgY"

# ── busca ─────────────────────────────────────────────────────
ORIGEM          = os.environ.get("ORIGEM", "BSB")
ADULTOS         = int(os.environ.get("ADULTOS", "2"))
PRECO_MIN       = float(os.environ.get("PRECO_MIN", "500"))
PRECO_MAX       = float(os.environ.get("PRECO_MAX", "1000"))
INTERVALO_HORAS = int(os.environ.get("INTERVALO_HORAS", "1"))

# ── destinos ──────────────────────────────────────────────────
DESTINOS = [
    # Brasil
    "GRU", "GIG", "SSA", "FOR", "REC", "BEL",
    "MAO", "CWB", "POA", "FLN", "CNF", "MCZ",
    "NAT", "THE", "SDU", "CGH",
    # Internacional
    "MIA", "BOG", "LIM", "SCL", "EZE",
    "LIS", "MAD", "ORY",
]