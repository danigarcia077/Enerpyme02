import os
import calendar
import datetime as dt
import requests
import pandas as pd

os.makedirs("data/raw", exist_ok=True)
URL = "https://servapibi.xm.com.co/hourly"
hoy = dt.date.today()
ANO = hoy.year


def pedir(metrica, entidad, inicio, fin):
    cuerpo = {"MetricId": metrica, "StartDate": inicio, "EndDate": fin,
              "Entity": entidad, "Filter": []}
    r = requests.post(URL, json=cuerpo, timeout=60)
    r.raise_for_status()
    filas = []
    for item in r.json().get("Items", []):
        for ent in item.get("HourlyEntities", []):
            fila = {"Date": item["Date"], "Id": ent.get("Id")}
            for hora, valor in ent["Values"].items():
                fila["Values_" + hora] = valor
            filas.append(fila)
    tabla = pd.DataFrame(filas)
    if tabla.empty:
        return tabla
    cols = [c for c in tabla.columns if c.startswith("Values_")]
    tabla[cols] = tabla[cols].apply(pd.to_numeric, errors="coerce")
    return tabla


for metrica, nombre in [("PrecBolsNaci", f"precio_bolsa_{ANO}"),
                        ("DemaReal", f"demanda_real_{ANO}")]:
    partes = []
    for mes in range(1, hoy.month + 1):
        ultimo = calendar.monthrange(ANO, mes)[1]
        fin = min(dt.date(ANO, mes, ultimo), hoy)
        parte = pedir(metrica, "Sistema", f"{ANO}-{mes:02d}-01", fin.isoformat())
        if not parte.empty:
            partes.append(parte)
        print(nombre, "mes", mes, "listo")
    tabla = pd.concat(partes, ignore_index=True)
    tabla.to_csv(f"data/raw/{nombre}.csv", index=False)
    print(nombre, "filas:", len(tabla), "| último día:", tabla["Date"].max())

print("Listo: datos de XM actualizados hasta hoy")