# EnerPyme Analytics

**Plataforma de análisis de datos energéticos para PYMEs colombianas**
Proyecto final de la materia *Transmisión de datos*.

**Autoras:** Daniela García Valencia y Mariana Otalvaro Gutierrez

> "Transformamos fuentes de datos abiertas en decisiones estratégicas de ahorro para la PYME colombiana."

---

## 1. ¿Qué problema resuelve?

Las empresas tienen datos energéticos, pero no información útil:

- **Datos dispersos:** fuentes públicas (XM, datos.gov.co) y privadas en archivos aislados.
- **Falta de claridad:** no se puede comparar el consumo ni saber qué genera picos de costo.
- **Gestión reactiva:** el sobrecosto se conoce cuando llega la factura.

EnerPyme unifica estas fuentes y las convierte en indicadores para decidir. **No vende energía: vende inteligencia a partir de la energía.**

## 2. Flujo técnico (pipeline)

```
XM + datos.gov.co  ->  Extracción (Python)  ->  Limpieza (Pandas / ETL)
   ->  Base de datos SQL (SQLite)  ->  KPIs (Python / SQL)  ->  Dashboard (Power BI)  ->  Decisiones
```

| Etapa | Herramienta | Script |
|---|---|---|
| Extracción XM | Python + `requests` (API de XM) | `extraccion_xm_2026.py` |
| Extracción costo unitario | Python + `sodapy` (datos.gov.co), descarga por bloques con reintentos | `explorar_chec.py` |
| Limpieza / ETL | Pandas | `limpieza.py` |
| Almacenamiento | SQLite (`enerpyme.db`) | `crear_bd.py` |
| Facturas del cliente (simuladas) | Pandas + NumPy | `facturas_simuladas.py` |
| Análisis y KPIs | Python + SQL | `kpis.py` |
| Exportación para Power BI | Pandas | `exportar_powerbi.py` |
| Dashboard | Power BI Desktop | `EnerPyme_Dashboard.pbix` / `.pdf` |
| Orquestación (un solo comando) | Python | `actualizar_todo.py` |
| Automatización diaria | Programador de tareas de Windows | `actualizar.bat` |
| Prueba de las fuentes en vivo | Python | `probar_fuentes.py` |

Todo el software usado es gratuito o de código abierto (Power BI Desktop es gratuito).

## 3. Fuentes de datos

| Fuente | Qué aporta | Cobertura |
|---|---|---|
| **XM** (API `servapibi.xm.com.co`), variables `PrecBolsNaci` y `DemaReal` | Precio de bolsa nacional (COP/kWh) y demanda real del país (kWh), por hora | Del 1 de enero del año en curso hasta el último día publicado (XM publica con 1 o 2 días de retraso) |
| **datos.gov.co**, conjunto "Información Costo unitario de tarifas de energía CHEC" (`c698-wqig`) | Costo unitario (CU) de la energía en $/kWh, con sus componentes, por clase de servicio y nivel de tensión | 2015 - sep 2026 (publicación mensual; se usan 2025-2026, clases Comercial e Industrial) |
| **Facturas simuladas** | Consumo de una empresa ficticia con 3 sedes | ene - sep 2026 |

## 4. Estructura del proyecto

```
EnerPyme/
├── extraccion_xm_2026.py     # descarga precio de bolsa y demanda (XM) hasta hoy
├── explorar_chec.py          # descarga el costo unitario de CHEC (por bloques) y lo explora
├── limpieza.py               # ETL: deja los datos limpios en data/clean
├── crear_bd.py               # crea enerpyme.db y carga las tablas
├── facturas_simuladas.py     # genera las facturas sintéticas
├── kpis.py                   # calcula los indicadores
├── exportar_powerbi.py       # CSV con ; y coma decimal para Power BI en español
├── actualizar_todo.py        # ejecuta todo el pipeline en orden
├── actualizar.bat            # lanza actualizar_todo.py y guarda el registro en actualizacion.log
├── probar_fuentes.py         # comprueba que XM y datos.gov.co respondan y hasta qué fecha
├── revisar_conjunto.py       # utilidad: inspecciona cualquier conjunto de datos.gov.co
├── actualizacion.log         # registro de las ejecuciones automáticas
├── enerpyme.db               # base de datos SQLite
├── EnerPyme_Dashboard.pbix   # dashboard (Power BI)
├── EnerPyme_Dashboard.pdf    # copia del dashboard en PDF
└── data/
    ├── raw/                  # datos crudos, sin modificar
    ├── clean/                # datos limpios
    └── powerbi/              # CSV listos para Power BI
```

## 5. Cómo ejecutarlo

Requisitos: **Python 3.14** (probado con 3.14.8) y conexión a internet.

### Instalación (una sola vez)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install pandas requests sodapy matplotlib
```

### Actualizar todo con un solo comando

```powershell
python actualizar_todo.py
```

Ejecuta en orden: `extraccion_xm_2026.py`, `explorar_chec.py`, `limpieza.py`, `crear_bd.py`, `facturas_simuladas.py`, `kpis.py` y `exportar_powerbi.py`. Si un paso falla, se detiene e indica cuál. Al terminar, en Power BI hay que abrir `EnerPyme_Dashboard.pbix` y hacer clic en **Inicio > Actualizar**.

También se puede ejecutar haciendo doble clic en `actualizar.bat`; el resultado queda al final de `actualizacion.log`.

### Actualización automática diaria

Se configuró una tarea en el **Programador de tareas de Windows** ("EnerPyme actualización") que ejecuta `actualizar.bat` cada día. Requisitos: el computador debe estar encendido (la tarea está configurada para ejecutarse apenas se pueda si estaba apagado a la hora programada). Nota: `actualizar.bat` tiene escrita la ruta `C:\Users\HP\Documents\EnerPyme`; si el proyecto se mueve de carpeta, hay que cambiarla.

### Comprobar que las fuentes responden

```powershell
python probar_fuentes.py
```

Consulta XM y datos.gov.co en ese momento e indica el último día (XM) y el último periodo (CHEC) disponibles, sin modificar los datos del proyecto.

## 6. Dashboard

| Página | Pregunta que responde |
|---|---|
| **Mercado** | ¿Cómo cambió el precio de bolsa? ¿La tarifa regulada lo amortigua? |
| **Consumo por sede** | ¿Qué sede consume más y en qué meses? |
| **Consumo vs. precio** | ¿La factura subió por consumo o por costo por kWh? (julio vs. junio) |
| **Demanda nacional** | ¿Cómo se comporta la demanda eléctrica del país? |

## 7. Resultados principales (enero - septiembre 2026)

- **El precio de bolsa es muy volátil:** pasó de ~212 COP/kWh en enero a ~942 en agosto, con variaciones mensuales entre -41% y +88%.
- **El costo unitario de CHEC es mucho más estable:** variaciones mensuales entre -5,5% y +5,7%, y un aumento de ~65 $/kWh entre enero y septiembre. La tarifa regulada amortigua parte de la volatilidad de la bolsa.
- **El alza del costo unitario se explica casi toda por la generación** (+90 $/kWh), compensada en parte por restricciones (-17) y transmisión (-9).
- **Correlación bolsa vs. costo unitario: 0,95**, calculada con solo 9 meses. Es un dato descriptivo y no prueba que una variable cause la otra.
- **Julio vs. junio (datos simulados):** en la bodega frigorífica el aumento de la factura se debió sobre todo al consumo; en la planta industrial pesó más el precio por kWh.

Estos resultados corresponden a los datos disponibles al 10 de octubre de 2026 (XM hasta el 8 de octubre; CHEC hasta septiembre). Cambiarán si las fuentes publican datos nuevos.

## 8. Limitaciones

- **El precio de bolsa no equivale a la tarifa facturada.** Se usa como referencia del mercado, no como costo del cliente.
- **Las facturas son simuladas.** El consumo (kWh) es inventado (semilla fija 42); solo el costo por kWh es real. El valor de la factura es `kWh x costo unitario` y no incluye impuestos, contribuciones ni cargos fijos. No existe una PYME real detrás de estos datos.
- **Las facturas simuladas y varios KPIs están fijados a enero-septiembre.** `facturas_simuladas.py` genera los meses 1 a 9, y la comparación 2025 vs. 2026 de `kpis.py` usa `mes <= 9`. Cuando CHEC publique más meses hay que ajustar esos valores.
- **Cambio de año:** los scripts toman el año actual para XM, pero `limpieza.py` lee archivos con "2026" en el nombre; en 2027 habría que actualizarlos.
- **El costo unitario proviene de una sola empresa** (CHEC, mercados CHEC y Pereira): es un caso piloto regional. La extensión a otras comercializadoras es una mejora futura.
- **Mercado regulado:** una PYME que negocia su energía directamente (mercado no regulado) puede pagar un valor distinto.
- **Comercial e Industrial tienen el mismo costo unitario** en este conjunto, por lo que no se pueden distinguir por costo.
- **Rezago de las fuentes:** XM publica con 1 o 2 días de retraso y CHEC por mes. El mes en curso queda incompleto y se excluye de las comparaciones mensuales.
- **Pocos datos para estadística:** 9 meses comparables. Las comparaciones 2025 vs. 2026 de enero y febrero de 2025 pueden no ser fiables (el conjunto tenía menos filas esos meses).
- **Preguntas que requieren mediciones más detalladas** (horarios de mayor consumo, proceso o equipo a revisar) no se pueden responder con facturas mensuales; necesitan registros por hora, proceso o equipo.
- **Power BI no se refresca solo:** la actualización automática cubre los datos y la base; el dashboard se refresca con el botón **Actualizar**. La actualización programada en la nube (Power BI Service) requiere cuenta institucional, licencia y puerta de enlace, y no se implementó.
- **Librería `pydataxm`:** no funciona con Python 3.14 (error interno de `nest_asyncio`), por lo que la extracción de XM se hace directamente con `requests`.

## 9. Decisiones de diseño

- Se descartó el conjunto "Superservicios - Costo Unitario Prestación del Servicio" porque solo contiene datos de 2023 y no se podía cruzar con XM 2026.
- Los datos crudos de `data/raw` nunca se modifican; la limpieza escribe en `data/clean`.
- Para Power BI en español se exportan copias con separador `;` y coma decimal, para que los números se lean bien sin cambiar la configuración regional.
- La descarga de datos.gov.co se hace por bloques de 5.000 filas con reintentos, porque una descarga única de 40.609 filas falló por un corte de conexión.

## 10. Página web con actualización diaria

La carpeta `docs/` contiene la página web del tablero (`docs/index.html`). Lee sus datos de `docs/data/datos.json`, que genera `exportar_web.py` a partir de `data/clean`.

- **Publicación:** GitHub Pages sirve la carpeta `docs/` del repositorio (Settings > Pages > Branch `main`, carpeta `/docs`).
- **Actualización diaria:** el flujo `.github/workflows/actualizar.yml` (GitHub Actions) corre cada día `actualizar_todo.py` y `exportar_web.py`, y guarda los datos nuevos en el repositorio. La página los muestra al abrirse. También se puede lanzar a mano desde la pestaña Actions.
- **Qué se actualiza solo:** los datos reales de XM y CHEC. Las facturas de las tres sedes son simuladas y no cambian.
- **Power BI:** el archivo `EnerPyme_Dashboard.pbix` sigue siendo el dashboard de Power BI Desktop. La página web reproduce sus cuatro páginas con gráficas propias; no inserta el Power BI publicado.
