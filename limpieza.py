import os
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
os.makedirs("data/clean", exist_ok=True)


def horas(df):
    return [c for c in df.columns if c.startswith("Values_")]


# ========== XM: de 24 columnas por hora a una fila por día ==========
precio = pd.read_csv("data/raw/precio_bolsa_2026.csv")
demanda = pd.read_csv("data/raw/demanda_real_2026.csv")

p = pd.DataFrame({
    "fecha": pd.to_datetime(precio["Date"]),
    "precio_bolsa_prom": precio[horas(precio)].mean(axis=1),
    "precio_bolsa_max": precio[horas(precio)].max(axis=1),
}).drop_duplicates("fecha")

d = pd.DataFrame({
    "fecha": pd.to_datetime(demanda["Date"]),
    "demanda_kwh": demanda[horas(demanda)].sum(axis=1, min_count=24),
}).drop_duplicates("fecha")

xm_dia = p.merge(d, on="fecha", how="outer").sort_values("fecha")
xm_dia.to_csv("data/clean/xm_diario.csv", index=False)

# Resumen mensual
xm_dia["periodo"] = xm_dia["fecha"].dt.to_period("M").dt.to_timestamp()
xm_mes = xm_dia.groupby("periodo").agg(
    dias=("fecha", "count"),
    precio_bolsa_prom=("precio_bolsa_prom", "mean"),
    precio_bolsa_max=("precio_bolsa_max", "max"),
    demanda_kwh=("demanda_kwh", "sum"),
).reset_index()
xm_mes["mes_completo"] = xm_mes["dias"] == xm_mes["periodo"].dt.days_in_month
xm_mes.to_csv("data/clean/xm_mensual.csv", index=False)

print("=== XM diario ===", xm_dia.shape, "| días sin dato:", xm_dia.isna().sum().sum())
print("\n=== XM mensual ===")
print(xm_mes.round(1))

# ========== CHEC: costo unitario de comercial e industrial ==========
chec = pd.read_csv("data/raw/costo_unitario_chec.csv")
chec.columns = [c.replace("costounitariotarifa_", "") for c in chec.columns]

numericas = ["ano", "mes", "generacion", "transmision", "distribucion",
             "comercializacion", "perdidas", "restricciones", "cu", "valor_tarifa"]
chec[numericas] = chec[numericas].apply(pd.to_numeric, errors="coerce")

chec = chec[(chec["ano"] >= 2025) & (chec["claseservicio_codigo"].isin(["CR", "ID"]))].copy()
chec["periodo"] = pd.to_datetime(dict(year=chec["ano"], month=chec["mes"], day=1))

columnas = ["periodo", "ano", "mes", "mercado_nombre", "nivel_tension_codigo",
            "modalidadcobro_propiedad", "tipomed", "claseservicio_codigo",
            "claseservicio_descri", "generacion", "transmision", "distribucion",
            "comercializacion", "perdidas", "restricciones", "cu", "valor_tarifa"]
chec = chec[columnas]

antes = len(chec)
chec = chec.drop_duplicates()
print("\n=== CHEC ===", chec.shape, "| duplicados eliminados:", antes - len(chec))
print("Costo unitario <= 0:", (chec["cu"] <= 0).sum(), "filas")
print("Valores vacíos:\n", chec.isna().sum()[chec.isna().sum() > 0])

chec.to_csv("data/clean/chec_cu_limpio.csv", index=False)

print("\n=== CU promedio por mes y clase (2026) ===")
print(chec[chec["ano"] == 2026].groupby(["periodo", "claseservicio_codigo"])["cu"].mean().round(1).unstack())

print("\nListo: archivos guardados en data/clean")