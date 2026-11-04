import os
import time
import pandas as pd
from sodapy import Socrata

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 100)

os.makedirs("data/raw", exist_ok=True)

cliente = Socrata("www.datos.gov.co", None, timeout=120)


def descargar(id_conjunto, tam=5000, reintentos=5):
    """Descarga el conjunto por bloques; si un bloque falla, lo reintenta."""
    filas = []
    offset = 0
    while True:
        for intento in range(1, reintentos + 1):
            try:
                bloque = cliente.get(id_conjunto, limit=tam, offset=offset, order=":id")
                break
            except Exception as e:
                print(f"Fallo en el bloque {offset} (intento {intento}/{reintentos}): {type(e).__name__}")
                if intento == reintentos:
                    raise
                time.sleep(3 * intento)
        if not bloque:
            break
        filas.extend(bloque)
        print("Filas descargadas:", len(filas))
        if len(bloque) < tam:
            break
        offset += tam
    return pd.DataFrame.from_records(filas)


df = descargar("c698-wqig")
df.to_csv("data/raw/costo_unitario_chec.csv", index=False)
print("Filas y columnas:", df.shape)

df["ano"] = pd.to_numeric(df["costounitariotarifa_ano"])
df["mes"] = pd.to_numeric(df["costounitariotarifa_mes"])

print("\n=== Meses disponibles en 2025 y 2026 (filas por mes) ===")
print(df[df["ano"] >= 2025].groupby(["ano", "mes"]).size())

reciente = df[df["ano"] >= 2025]

print("\n=== Clases de servicio (2025-2026) ===")
print(reciente.groupby(["claseservicio_codigo", "claseservicio_descri"]).size())

print("\n=== Mercados ===")
print(reciente["mercado_nombre"].value_counts())

print("\n=== Códigos de nivel de tensión ===")
print(reciente["nivel_tension_codigo"].value_counts())

print("\n=== Tipo de medida (tipomed) ===")
print(reciente["costounitariotarifa_tipomed"].value_counts())

print("\n=== Costo unitario (cu) por clase en 2026 ===")
d26 = df[df["ano"] == 2026].copy()
d26["cu"] = pd.to_numeric(d26["costounitariotarifa_cu"])
print(d26.groupby("claseservicio_descri")["cu"].agg(["count", "mean", "min", "max"]).round(1))