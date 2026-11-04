import sys
import pandas as pd
from sodapy import Socrata

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

id_conjunto = sys.argv[1]
cliente = Socrata("www.datos.gov.co", None, timeout=60)
df = pd.DataFrame.from_records(cliente.get(id_conjunto, limit=50000))

print("Filas y columnas:", df.shape)
print("Columnas:", list(df.columns))
print(df.head())
for c in df.columns:
    if "ano" in c.lower() or "anio" in c.lower() or "fecha" in c.lower() or "periodo" in c.lower():
        print("\nValores de", c)
        print(df[c].astype(str).str[:7].value_counts().sort_index().tail(12))