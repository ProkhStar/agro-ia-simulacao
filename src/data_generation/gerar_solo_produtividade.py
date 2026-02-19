# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

np.random.seed(123)

talhoes = pd.read_csv("data/synthetic/talhoes.csv")
clima = pd.read_csv("data/synthetic/clima_diario_2019_2024.csv", parse_dates=["data"])

print("📂 Dados carregados:")
print(f"   - {len(talhoes)} talhões")
print(f"   - {len(clima)} dias de clima")

solo_params = {
    "xisto": {
        "ph": (5.5, 6.5),
        "mo_perc": (1.5, 3.0),
        "argila_perc": (15, 25),
        "limo_perc": (20, 30),
        "areia_perc": (45, 65),
        "capacidade_agua": (100, 150)
    },
    "xisto_argila": {
        "ph": (5.8, 6.8),
        "mo_perc": (2.0, 3.5),
        "argila_perc": (25, 35),
        "limo_perc": (25, 35),
        "areia_perc": (30, 50),
        "capacidade_agua": (130, 180)
    }
}

solo_data = []
for _, talhao in talhoes.iterrows():
    tipo = talhao["solo"]
    params = solo_params.get(tipo, solo_params["xisto"])
    
    solo = {
        "talhao_id": talhao["id"],
        "ph": np.random.uniform(*params["ph"]),
        "mo_perc": np.random.uniform(*params["mo_perc"]),
        "argila_perc": np.random.uniform(*params["argila_perc"]),
        "limo_perc": np.random.uniform(*params["limo_perc"]),
        "areia_perc": np.random.uniform(*params["areia_perc"]),
        "capacidade_agua_mm": np.random.uniform(*params["capacidade_agua"]),
    }
    solo_data.append(solo)

solo_df = pd.DataFrame(solo_data)
print("✅ Características de solo geradas.")

talhoes_com_solo = talhoes.merge(solo_df, left_on="id", right_on="talhao_id", how="left")
talhoes_com_solo.to_csv("data/synthetic/talhoes_com_solo.csv", index=False)
print("✅ Ficheiro talhoes_com_solo.csv criado.")

anos = range(2019, 2025)
produtividade_anual = []

for ano in anos:
    inicio = pd.Timestamp(f"{ano}-04-01")
    fim = pd.Timestamp(f"{ano}-09-30")
    clima_ciclo = clima[(clima["data"] >= inicio) & (clima["data"] <= fim)]
    
    graus_dia = np.sum(np.maximum(0, clima_ciclo["t_mean"] - 10))
    precip_total = clima_ciclo["precip_mm"].sum()
    
    for _, talhao in talhoes_com_solo.iterrows():
        fator_casta = {
            "Touriga Nacional": 1.0,
            "Tinta Roriz": 1.1,
            "Touriga Franca": 1.05,
            "Viosinho": 0.9,
            "Tinto Cão": 0.85
        }.get(talhao["casta"], 1.0)
        
        fator_solo = 0.5 + 0.3 * (talhao["capacidade_agua_mm"] / 150) + 0.2 * (talhao["mo_perc"] / 3)
        
        prod_base = (0.005 * graus_dia + 0.1 * precip_total - 5) * fator_casta * fator_solo
        
        ruido = np.random.normal(1.0, 0.15)
        prod_final = max(0.5, prod_base * ruido)
        
        produtividade_anual.append({
            "ano": ano,
            "talhao_id": talhao["id"],
            "casta": talhao["casta"],
            "produtividade_ton_ha": round(prod_final, 2),
            "graus_dia_ciclo": round(graus_dia),
            "precip_ciclo_mm": round(precip_total, 1)
        })

prod_df = pd.DataFrame(produtividade_anual)
prod_df.to_csv("data/synthetic/produtividade_anual.csv", index=False)
print("✅ Ficheiro produtividade_anual.csv criado.")

ndvi_registos = []

for _, talhao in talhoes_com_solo.iterrows():
    talhao_id = talhao["id"]
    
    for _, row in clima.iterrows():
        data = row["data"]
        dia_ano = data.dayofyear
        
        ndvi_base = 0.3 + 0.5 * np.exp(-((dia_ano - 180) / 60) ** 2)
        
        ultimos_30 = clima[(clima["data"] <= data) & (clima["data"] > data - pd.Timedelta(days=30))]
        precip_30d = ultimos_30["precip_mm"].sum()
        fator_stress = min(1.0, 0.7 + 0.3 * (precip_30d / 100))
        
        ruido = np.random.normal(1.0, 0.05)
        
        ndvi = ndvi_base * fator_stress * ruido
        ndvi = np.clip(ndvi, 0.2, 0.9)
        
        ndvi_registos.append({
            "data": data,
            "talhao_id": talhao_id,
            "ndvi": round(ndvi, 3)
        })

ndvi_df = pd.DataFrame(ndvi_registos)
ndvi_df.to_csv("data/synthetic/ndvi_diario.csv", index=False)
print("✅ Ficheiro ndvi_diario.csv criado.")

print("\n🎉 Geração de dados de solo e produtividade concluída!")
