"""Crea docs/data/datos.json con los datos que usa la pagina web.

Lee los CSV limpios de data/clean (los que genera el resto del proyecto)
y los deja en un solo archivo JSON dentro de docs/data.
"""
import json
import datetime as dt
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
CLEAN = BASE / "data" / "clean"
SALIDA = BASE / "docs" / "data"

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
COMPONENTES = {
    "generacion": "Generación",
    "perdidas": "Pérdidas",
    "comercializacion": "Comercialización",
    "distribucion": "Distribución",
    "transmision": "Transmisión",
    "restricciones": "Restricciones",
}


def nombre_mes(texto):
    """'2026-08' o '2026-08-01' -> 'Ago'."""
    return MESES[int(str(texto)[5:7]) - 1]


def valor(x, decimales=2):
    """Numero redondeado, o texto vacio si no hay dato."""
    return "" if pd.isna(x) else round(float(x), decimales)


kpis = pd.read_csv(CLEAN / "kpis_mensuales.csv")
xm = pd.read_csv(CLEAN / "xm_mensual.csv")
chec = pd.read_csv(CLEAN / "chec_cu_limpio.csv", usecols=["periodo"])
fac = pd.read_csv(CLEAN / "facturas_simuladas.csv")

# 1. Mercado: precio de bolsa, costo unitario y demanda por mes
mercado = []
for _, f in kpis.iterrows():
    mes = str(f["mes"])[:7]
    mercado.append({
        "mes": mes,
        "mes_nombre": nombre_mes(mes),
        "precio_bolsa": valor(f["precio_bolsa"], 1),
        "cu_chec": valor(f["cu"], 1),
        "demanda_gwh": valor(f["demanda_kwh"] / 1e6, 3),
        "var_bolsa_pct": valor(f["precio_bolsa_var_%"], 1),
        "var_cu_pct": valor(f["cu_var_%"], 1),
    })

# 2. Cambio de cada componente del costo unitario (primer mes -> ultimo mes)
componentes = []
for col, etiqueta in COMPONENTES.items():
    cambio = float(kpis[col].iloc[-1]) - float(kpis[col].iloc[0])
    componentes.append({"componente": etiqueta, "cambio_cop_kwh": round(cambio, 1)})
componentes.sort(key=lambda d: d["cambio_cop_kwh"], reverse=True)

# 3. Facturas simuladas por sede y mes
fac["mes_txt"] = fac["periodo"].astype(str).str[:7]
sedes = []
for _, f in fac.sort_values(["sede", "mes_txt"]).iterrows():
    sedes.append({
        "mes": f["mes_txt"],
        "mes_nombre": nombre_mes(f["mes_txt"]),
        "sede": f["sede"],
        "consumo_kwh": int(round(f["consumo_kwh"])),
        "factura_cop": int(round(f["valor_factura"])),
    })

# 4. Julio frente a junio: efecto consumo y efecto precio
julio = fac[fac["mes"] == 7].sort_values("cambio_factura", ascending=False)
efecto = []
for _, f in julio.iterrows():
    efecto.append({
        "sede": f["sede"],
        "var_consumo_pct": valor(f["var_consumo_%"], 1),
        "cambio_factura": int(round(f["cambio_factura"])),
        "efecto_consumo": int(round(f["efecto_consumo"])),
        "efecto_precio": int(round(f["efecto_precio"])),
    })

# 5. Hasta cuando llegan los datos
ultimo = xm.iloc[-1]
xm_hasta = pd.to_datetime(ultimo["periodo"]) + pd.Timedelta(days=int(ultimo["dias"]) - 1)
chec_hasta = str(chec["periodo"].astype(str).max())[:7]
estado = [{
    "xm_hasta": xm_hasta.strftime("%Y-%m-%d"),
    "chec_hasta": chec_hasta,
    "cargado": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
}]

SALIDA.mkdir(parents=True, exist_ok=True)
datos = {
    "mercado": mercado,
    "componentes": componentes,
    "sedes": sedes,
    "efecto": efecto,
    "estado": estado,
}
with open(SALIDA / "datos.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False)

print(f"Listo: docs/data/datos.json | meses de mercado: {len(mercado)} | "
      f"XM hasta {estado[0]['xm_hasta']} | CHEC hasta {chec_hasta}")
