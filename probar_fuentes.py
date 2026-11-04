import datetime as dt
import requests
import pandas as pd
from sodapy import Socrata

hoy = dt.date.today()
print("Fecha de hoy:", hoy)

print("\n=== XM (API en vivo) ===")
cuerpo = {
    "MetricId": "PrecBolsNaci",
    "StartDate": (hoy - dt.timedelta(days=10)).isoformat(),
    "EndDate": hoy.isoformat(),
    "Entity": "Sistema",
    "Filter": [],
}
r = requests.post("https://servapibi.xm.com.co/hourly", json=cuerpo, timeout=60)
print("Código de respuesta:", r.status_code, "(200 = bien)")
fechas = [item["Date"] for item in r.json().get("Items", [])]
print("Días recibidos:", len(fechas))
print("Último día disponible en XM:", max(fechas) if fechas else "ninguno")

print("\n=== datos.gov.co (conjunto de CHEC) ===")
cliente = Socrata("www.datos.gov.co", None, timeout=120)
bloque = cliente.get("c698-wqig", limit=1, order="costounitariotarifa_ano DESC, costounitariotarifa_mes DESC")
print("Respuesta recibida:", len(bloque) > 0)
if bloque:
    print("Último periodo publicado: año", bloque[0]["costounitariotarifa_ano"],
          "mes", bloque[0]["costounitariotarifa_mes"])