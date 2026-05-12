import os

# Configurações Gerais
DEBUG = os.environ.get("DEBUG", "False") == "True"
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

# Aeroportos de Origem (BSB, SP, RJ, PR)
AIRPORTS = {
    "BSB": ["BSB"],
    "SP": ["GRU", "CGH", "VCP", "RAO", "SJP", "PPB", "JTC", "MII"],
    "RJ": ["GIG", "SDU", "CFB", "CAW"],
    "PR": ["CWB", "LDB", "MGF", "IGU", "CAC"]
}

# Países prioritários para o canal #internacional
PRIORITY_COUNTRIES = ["Japão", "Espanha", "Colômbia", "Peru", "Itália", "China", "Tailândia", "EUA"]
INTERVALO_HORAS = 1