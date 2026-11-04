import os
import pandas as pd

os.makedirs("data/powerbi", exist_ok=True)

archivos = ["kpis_mensuales", "xm_diario", "chec_cu_limpio", "facturas_simuladas"]

for nombre in archivos:
    df = pd.read_csv(f"data/clean/{nombre}.csv")
    # sep=";" y decimal="," es el formato que Power BI en español lee sin problemas
    df.to_csv(f"data/powerbi/{nombre}.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print("Exportado:", nombre, df.shape)

print("Listo: archivos en data/powerbi")