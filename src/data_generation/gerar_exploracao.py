# coding: utf-8
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configura��o para reprodutibilidade
np.random.seed(42)

# ------------------------------------------------------------
# 1. Definir os talh�es (caracter�sticas fixas)
# ------------------------------------------------------------
talhoes = pd.DataFrame([
    {"id": 1, "area_ha": 1.2, "exposicao": "Sul", "declive_perc": 15,
     "altitude_m": 250, "solo": "xisto", "casta": "Touriga Nacional"},
    {"id": 2, "area_ha": 0.8, "exposicao": "Sudoeste", "declive_perc": 20,
     "altitude_m": 300, "solo": "xisto", "casta": "Tinta Roriz"},
    {"id": 3, "area_ha": 1.5, "exposicao": "Norte", "declive_perc": 10,
     "altitude_m": 200, "solo": "xisto_argila", "casta": "Touriga Franca"},
    {"id": 4, "area_ha": 1.0, "exposicao": "Este", "declive_perc": 5,
     "altitude_m": 180, "solo": "xisto", "casta": "Viosinho"},
    {"id": 5, "area_ha": 0.7, "exposicao": "Oeste", "declive_perc": 25,
     "altitude_m": 320, "solo": "xisto", "casta": "Tinto C�o"},
])

# Criar diret�rio synthetic se n�o existir
os.makedirs("data/synthetic", exist_ok=True)

# Guardar talh�es
talhoes.to_csv("data/synthetic/talhoes.csv", index=False)
print("? Ficheiro talhoes.csv criado.")

# ------------------------------------------------------------
# 2. Gerar s�ries clim�ticas di�rias (2019-2024)
# ------------------------------------------------------------
start_date = datetime(2019, 1, 1)
end_date = datetime(2024, 12, 31)
dates = pd.date_range(start_date, end_date, freq='D')
n_days = len(dates)

# Temperatura: modelo sazonal (pico em julho, m�nimo em janeiro)
t_base = 15 + 10 * np.sin(2 * np.pi * dates.dayofyear / 365 - 1.5)  # -1.5 para pico em julho
t_max = t_base + 5 + np.random.normal(0, 2, n_days)
t_min = t_base - 5 + np.random.normal(0, 2, n_days)
t_mean = (t_max + t_min) / 2

# Precipita��o: modelo com probabilidade sazonal (mais chuva no inverno)
prob_chuva = 0.1 + 0.15 * np.cos(2 * np.pi * dates.dayofyear / 365)  # max ~0.25 no inverno
prob_chuva = np.clip(prob_chuva, 0.05, 0.3)

precip = np.zeros(n_days)
for i in range(n_days):
    if np.random.rand() < prob_chuva[i]:
        precip[i] = np.random.exponential(10)  # mm/dia (m�dia 10 mm num dia de chuva)

# Humidade relativa (influenciada pela chuva)
humidade = 60 + 20 * (precip > 0) + np.random.normal(0, 10, n_days)
humidade = np.clip(humidade, 30, 100)

# Radia��o solar (maior no ver�o)
radiacao = 200 + 150 * np.sin(2 * np.pi * dates.dayofyear / 365 - 1.5) + np.random.normal(0, 30, n_days)
radiacao = np.clip(radiacao, 50, 400)

# Criar DataFrame
clima = pd.DataFrame({
    "data": dates,
    "t_max": t_max.round(1),
    "t_min": t_min.round(1),
    "t_mean": t_mean.round(1),
    "precip_mm": precip.round(1),
    "humidade_perc": humidade.round(1),
    "radiacao_w_m2": radiacao.round(1)
})

# Guardar
clima.to_csv("data/synthetic/clima_diario_2019_2024.csv", index=False)
print("? Ficheiro clima_diario_2019_2024.csv criado.")

print("\n?? Gera��o conclu�da com sucesso!")
