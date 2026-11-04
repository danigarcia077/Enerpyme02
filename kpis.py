import sqlite3
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

con = sqlite3.connect("enerpyme.db")

# Tabla mensual: XM + CU de CHEC (comercial, promedio de todos los niveles de tensión)
base = pd.read_sql_query("""
SELECT substr(x.periodo,1,7) AS mes,
       x.precio_bolsa_prom   AS precio_bolsa,
       x.demanda_kwh         AS demanda_kwh,
       AVG(c.cu)             AS cu,
       AVG(c.generacion)     AS generacion,
       AVG(c.transmision)    AS transmision,
       AVG(c.distribucion)   AS distribucion,
       AVG(c.comercializacion) AS comercializacion,
       AVG(c.perdidas)       AS perdidas,
       AVG(c.restricciones)  AS restricciones
FROM xm_mensual x
JOIN chec_cu c ON substr(x.periodo,1,7) = substr(c.periodo,1,7)
WHERE c.claseservicio_codigo = 'CR' AND x.mes_completo = 1
GROUP BY x.periodo ORDER BY x.periodo
""", con)

# 1) Variación porcentual mes a mes
for col in ["precio_bolsa", "demanda_kwh", "cu"]:
    base[col + "_var_%"] = (base[col].pct_change() * 100).round(1)

print("=== KPIs mensuales (variación % vs mes anterior) ===")
print(base[["mes", "precio_bolsa", "precio_bolsa_var_%", "demanda_kwh_var_%",
            "cu", "cu_var_%"]].round(1))

# 2) Qué componente explica el cambio del CU (enero -> septiembre)
comp = ["generacion", "transmision", "distribucion",
        "comercializacion", "perdidas", "restricciones"]
primero, ultimo = base.iloc[0], base.iloc[-1]
cambio = pd.DataFrame({
    "enero": primero[comp], "septiembre": ultimo[comp],
})
cambio["cambio_$/kWh"] = cambio["septiembre"] - cambio["enero"]
print("\n=== Cambio por componente del CU, enero -> septiembre ($/kWh) ===")
print(cambio.round(1))
print("Cambio total CU:", round(ultimo["cu"] - primero["cu"], 1))

# 3) Correlación bolsa vs CU
print("\nCorrelación precio de bolsa vs CU:",
      round(base["precio_bolsa"].corr(base["cu"]), 2), "(solo 9 meses)")

# 4) Comparación 2025 vs 2026 del CU (mismos meses)
cu = pd.read_sql_query("""
SELECT ano, mes, AVG(cu) AS cu FROM chec_cu
WHERE claseservicio_codigo='CR' AND mes <= 9 GROUP BY ano, mes
""", con)
tabla = cu.pivot(index="mes", columns="ano", values="cu")
tabla["var_%"] = ((tabla[2026] / tabla[2025] - 1) * 100).round(1)
print("\n=== CU 2025 vs 2026 por mes ===")
print(tabla.round(1))

base.to_csv("data/clean/kpis_mensuales.csv", index=False)
con.close()