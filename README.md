# ¿Qué estadísticas explican que un equipo de la NBA llegue a playoffs?

Proyecto final de Ciencia de Datos con Python.
**Integrantes:** Mauricio Villafañe y Santiago de la Hoz.
**Institución:** Universidad Americana de Barranquilla, Facultad de Ingeniería de Sistemas.
**Docente:** Edgar Morillo Vergel. **Periodo:** 7.º semestre.

**Repositorio:** https://github.com/ctlucifer1504-bit/proyecto_ciencia_de_datos

## Problema

Clasificación binaria: dado el perfil estadístico de un equipo en una temporada
regular (2000–2026), predecir si clasificó a playoffs y qué estadísticas de juego
pesan más. Los predictores son relativos al promedio de la liga en cada temporada.

## Fuente de datos y atribución

**Datos: Sports Reference LLC / Basketball-Reference.com.**

Basketball-Reference (una página por temporada, `/leagues/NBA_AAAA.html`).
Extracción con pausas de 4 s y caché local (límite del sitio: 20 peticiones/minuto).

> **Los datos no se incluyen en este repositorio.** No se publican HTML, CSV crudos,
> fragmentos, el dataset procesado ni predicciones fila a fila. Se publican el código,
> la documentación, las figuras y las métricas agregadas. Para reproducir el proyecto,
> ejecuta la extracción descrita en `data/README.md`.
>
> Los datos **no** están cubiertos por las licencias del código ni de la documentación.
> Consulta `docs/CONSIDERACIONES_LEGALES.md` antes de reutilizarlos.

## Estructura

- `scraping.py`    Fase I: extracción iterativa (`for` sobre temporadas) → `data/raw/`
- `limpieza.py`    Fase II: `pd.concat`, duplicados, nulos, tipos, filtros → `data/processed/`
- `exploracion.py` Fase III: gráficos y estadísticas → `outputs_corrida2_16vars/`
- `modelado.py`    Fase IV: modelo base, `GridSearchCV` (5 folds), test, robustez
                   → `outputs_corrida2_16vars_fase4/`
- `tests/`         Pruebas automáticas; las que requieren datos se omiten si no existen
- `docs/`          Informes de fase, diccionario, rúbrica, guion y declaración de IA
- `data/`          **No versionado**; solo `data/README.md` con instrucciones

## Estado actual

| Fase | Estado | Evidencia |
|---|---|---|
| I. Scraping | Ejecutada y verificada | `outputs/logs/scrape_log.csv` |
| II. Limpieza | Ejecutada y verificada | `outputs/metrics/limpieza_resumen.csv` |
| III. EDA (16 predictores) | Ejecutada y verificada | `outputs_corrida2_16vars/`, `docs/FASE_III_EDA_16VARS.md` |
| IV. Modelado (16 predictores) | Ejecutada y verificada | `outputs_corrida2_16vars_fase4/`, `docs/FASE_IV_MODELADO_16VARS.md` |

## Los 16 predictores

```text
off_eFG%, off_TOV%, off_ORB%, off_FT/FGA,
def_eFG%, def_TOV%, def_DRB%, def_FT/FGA,
Age, Pace, 3PAr, 3P%, FT%, AST, BLK, TRB
```

Variable objetivo: `playoffs` (0/1).

## Resultados principales (Fase IV, 16 predictores)

Protocolo principal: entrenamiento con temporadas 2000–2019 (595 filas) y test con
2020–2026 (210 filas), validación cruzada agrupada por temporada.

**Cifra titular:** umbral 0,50, que es el punto de corte estándar. El umbral elegido en
validación interna (0,46) se reporta como análisis secundario, porque cambia entre
protocolos y en el estratificado empeora el F1.

| Modelo (umbral 0,50) | CV F1 | Test F1 | Test accuracy | Test ROC-AUC | Brier |
|---|---:|---:|---:|---:|---:|
| Logística base (`C=1`) | 0,908 ± 0,007 | **0,879** | **0,862** | **0,946** | 0,099 |
| Logística optimizada (`C=0.1`) | 0,912 ± 0,009 | 0,866 | 0,848 | 0,942 | **0,097** |

Análisis secundario con umbral 0,46 (elegido en validación interna): F1 0,880,
accuracy 0,862, ROC-AUC 0,942. No supera al base; se documenta como sensibilidad.

- La regresión logística supera al Random Forest.
- `GridSearchCV` mejora +0,004 en validación cruzada y **no mejora en test**: se reporta así.
- Sobre test se calcularon tres variantes (base 0,50; optimizado 0,50; optimizado con umbral
  interno) solo para reporte. Ningún modelo, hiperparámetro ni umbral se eligió con test.
- Variables más importantes por permutación: `def_eFG%`, `def_TOV%`, `off_FT/FGA`, `off_TOV%`.
- Multicolinealidad alta: `TRB` (VIF 20,9), `Pace` (10,7) y `off_ORB%` (10,4).
- Informe completo: `docs/FASE_IV_MODELADO_16VARS.md`.

## Corridas históricas (no son el resultado actual)

`outputs/` y `outputs_corrida1_19vars/` contienen la **corrida histórica de 19 variables**
(incluía `FTr`, `PF` y `STL`). No deben presentarse como resultados actuales.
Ver `docs/RESPALDO_19VARS.md`. La comparación entre ambas corridas es descriptiva y
no controlada.

## Cómo ejecutar

Todos los comandos se ejecutan **desde la raíz del proyecto**.

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scraping.py      # Fase I: ~2 min con pausas de 4 s
python limpieza.py      # Fase II
python exploracion.py   # Fase III: ~10 s
python modelado.py      # Fase IV: ~1 min
python -m unittest discover -s tests -v
```

En un **clon limpio** no existe `data/`: el flujo empieza por `scraping.py`, que descarga
las 27 páginas y genera los fragmentos. No hay atajos con datos incluidos.

Si el sitio responde 403/429, guardar la página desde el navegador como
`data/raw/html/NBA_AAAA.html`; el script usa esos archivos sin hacer peticiones.

Las versiones exactas usadas en la corrida documentada están fijadas en
`requirements.txt` (Python 3.15.2). Ver también `docs/REPRODUCIBILIDAD.md`.

### Pruebas sin datos

Las pruebas de integridad del dataset, de variables relativas y del pipeline se **omiten
con un mensaje claro** si falta `data/processed/nba_teams_clean.csv`. Las pruebas de
predictores y de artefactos de Fase IV sí se ejecutan. Para correr la suite completa,
genera primero los datos con `scraping.py` y `limpieza.py`.

## Limitaciones

Cobertura 2000–2026; una sola fuente (Basketball-Reference); cambios de formato de
playoffs (play-in desde 2021); temporadas con menos de 82 partidos (2012, 2020 y 2021;
en 2013 dos equipos jugaron 81); variables relativas calculadas con el promedio de la
temporada (transformación transductiva, declarada); test pequeño (210 temporal, 161
estratificado); importancia por permutación calculada en una validación interna de 119
filas, con intervalos anchos; multicolinealidad alta; `best_score_` optimista por falta
de validación anidada; asociación no es causalidad; observaciones no independientes
entre temporadas del mismo equipo.

## Licencias

- **Código:** MIT. Ver `LICENSE`.
- **Documentación e informes (`docs/`):** CC BY 4.0. Ver `LICENSE-DOCS.md`.
- **Datos:** © Sports Reference LLC. **No** están cubiertos por MIT ni CC BY 4.0 y no se
  redistribuyen en este repositorio. Atribución: *Datos: Sports Reference LLC /
  Basketball-Reference.com*.

## Consideraciones legales y éticas

El proyecto usa datos públicos de Basketball-Reference con fines educativos. Los términos
de Sports Reference (cláusula 5(k), consultados el 2026-11-18) restringen el uso del
contenido para entrenar, ajustar o instruir modelos de IA, incluido el apoyo a métodos de
aprendizaje automático que predicen o clasifican. La página de uso de datos enfatiza la IA
generativa, por lo que el alcance sobre un trabajo académico de clasificación es ambiguo.
No se presenta esto como una autorización ni como una conclusión legal.

Mitigaciones aplicadas: no se redistribuyen datos crudos ni fila a fila; extracción a ritmo
bajo con pausa de 4 s y caché; sin datos personales; uso educativo; y declaración completa
de las herramientas de IA en `docs/DECLARACION_IA.md`.

Ver `docs/CONSIDERACIONES_LEGALES.md` para el texto citado, la incertidumbre y el detalle.

## Documentación

- `docs/FASE_III_EDA_16VARS.md` — EDA completo.
- `docs/FASE_IV_MODELADO_16VARS.md` — modelado, métricas y limitaciones.
- `docs/DICCIONARIO_DATOS.md` — definición de cada variable.
- `docs/MATRIZ_RUBRICA.md` — trazabilidad requisito → evidencia.
- `docs/INFORME_FINAL.md` — informe final.
- `docs/GUION_VIDEO.md` — guion de sustentación (≤ 15 min).
- `docs/DECLARACION_IA.md` — uso de asistencia de IA.
- `docs/CONTRIBUCIONES.md` — reparto de trabajo.
- `docs/REPRODUCIBILIDAD.md` — entorno y comandos.
- `docs/CONSIDERACIONES_LEGALES.md` — términos, ambigüedad y mitigaciones.
- `data/README.md` — cómo regenerar los datos (no incluidos).
