import subprocess
import sys

pasos = [
    "extraccion_xm_2026.py",   # XM hasta hoy
    "explorar_chec.py",        # costo unitario de datos.gov.co
    "limpieza.py",
    "crear_bd.py",
    "facturas_simuladas.py",
    "kpis.py",
    "exportar_powerbi.py",
]

for p in pasos:
    print(f"\n>>> Ejecutando {p}")
    resultado = subprocess.run([sys.executable, p])
    if resultado.returncode != 0:
        print(f"ERROR en {p}. Se detiene aquí.")
        sys.exit(1)

print("\nTodo actualizado. En Power BI haz clic en Actualizar.")