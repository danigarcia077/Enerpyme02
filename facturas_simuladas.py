import sqlite3
import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

rng = np.random.default_rng(42)  # semilla fija: siempre salen los mismos datos

# Costo unitario real de CHEC (clase comercial) por mes y nivel de tensión, 2026
chec = pd.read_csv("data/clean/chec_cu_limpio.csv", parse_dates=["periodo"])
chec = chec[(chec["ano"] == 2026) & (chec["claseservicio_codigo"] == "CR")]
cu = chec.groupby(["periodo", "nivel_tension_codigo"])["cu"].mean().reset_index()

# Sedes simuladas: consumo base mensual (kWh) y qué tanto varía con la época del año
sedes = [
    {"sede": "Planta industrial",  "tipo": "Industrial",  "nivel": 2, "base": 45000, "estacional": 0.05},
    {"sede": "Bodega frigorífica", "tipo": "Frigorífico", "nivel": 1, "base": 28000, "estacional": 0.20},
    {"sede": "Oficina comercial",  "tipo": "Comercial",   "nivel": 1, "base": 6000,  "estacional": 0.08},
]

filas = []
for s in sedes:
    for mes in range(1, 10):  # enero a septiembre
        periodo = pd.Timestamp(2026, mes, 1)
        fila_cu = cu[(cu["periodo"] == periodo) & (cu["nivel_tension_codigo"] == s["nivel"])]
        if fila_cu.empty:
            raise SystemExit(f"No hay CU para nivel {s['nivel']} en el mes {mes}")
        costo = float(fila_cu["cu"].iloc[0])

        factor = 1 + s["estacional"] * np.sin(2 * np.pi * (mes - 3) / 12)
        kwh = s["base"] * factor * (1 + rng.normal(0, 0.03))
        if s["sede"] == "Bodega frigorífica" and mes == 7:
            kwh *= 1.18  # consumo anormal simulado (por ejemplo, un equipo con falla)

        filas.append({"periodo": periodo, "mes": mes, "sede": s["sede"], "tipo": s["tipo"],
                      "nivel_tension": s["nivel"], "consumo_kwh": round(kwh),
                      "cu_kwh": round(costo, 1)})

df = pd.DataFrame(filas)
df["valor_factura"] = (df["consumo_kwh"] * df["cu_kwh"]).round(0)

# Cambio frente al mes anterior, separado en efecto consumo y efecto precio
df = df.sort_values(["sede", "periodo"]).reset_index(drop=True)
g = df.groupby("sede")
df["cambio_factura"] = df["valor_factura"] - g["valor_factura"].shift()
df["efecto_consumo"] = ((df["consumo_kwh"] - g["consumo_kwh"].shift()) * g["cu_kwh"].shift()).round(0)
df["efecto_precio"] = ((df["cu_kwh"] - g["cu_kwh"].shift()) * df["consumo_kwh"]).round(0)
df["var_consumo_%"] = (df["consumo_kwh"] / g["consumo_kwh"].shift() - 1).mul(100).round(1)

df.to_csv("data/clean/facturas_simuladas.csv", index=False)

con = sqlite3.connect("enerpyme.db")
df.to_sql("facturas_simuladas", con, if_exists="replace", index=False)
con.close()

print("Filas generadas:", len(df))
print("\n=== Consumo (kWh) por mes y sede ===")
print(df.pivot(index="mes", columns="sede", values="consumo_kwh"))
print("\n=== Valor de la factura ($) por mes y sede ===")
print(df.pivot(index="mes", columns="sede", values="valor_factura"))
print("\n=== Julio vs junio: ¿consumo o precio? ===")
print(df[df["mes"] == 7][["sede", "var_consumo_%", "cambio_factura", "efecto_consumo", "efecto_precio"]])
print("\nListo: facturas_simuladas.csv en data/clean y tabla en enerpyme.db")