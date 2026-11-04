import sqlite3
import pandas as pd

conexion = sqlite3.connect("enerpyme.db")

tablas = {
    "xm_diario": "data/clean/xm_diario.csv",
    "xm_mensual": "data/clean/xm_mensual.csv",
    "chec_cu": "data/clean/chec_cu_limpio.csv",
}

for nombre, ruta in tablas.items():
    df = pd.read_csv(ruta)
    df.to_sql(nombre, conexion, if_exists="replace", index=False)
    print("Tabla", nombre, "cargada:", len(df), "filas")

# Primera consulta SQL: precio de bolsa vs costo unitario CHEC por mes (2026)
consulta = """
SELECT substr(x.periodo, 1, 7)          AS mes,
       ROUND(x.precio_bolsa_prom, 1)    AS precio_bolsa,
       ROUND(AVG(c.cu), 1)              AS cu_chec
FROM xm_mensual x
JOIN chec_cu c
  ON substr(x.periodo, 1, 7) = substr(c.periodo, 1, 7)
WHERE c.claseservicio_codigo = 'CR'
  AND x.mes_completo = 1
GROUP BY x.periodo
ORDER BY x.periodo;
"""
print()
print(pd.read_sql_query(consulta, conexion))
conexion.close()