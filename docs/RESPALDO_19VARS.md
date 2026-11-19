# Respaldo e identificación de la corrida histórica de 19 variables

**Fecha de auditoría:** 2026-11-18  
**Objetivo:** separar los artefactos históricos de 19 predictores de la corrida actual de 16 predictores, sin borrar ni sobrescribir nada.

## 1. Qué se encontró

La carpeta `outputs/` contenía resultados de EDA y de modelado de una ejecución anterior. El EDA de esa ejecución usaba **19 predictores**: los 16 actuales más `FTr`, `PF` y `STL`. La evidencia está en:

- `outputs/metrics/eda_correlacion_objetivo.csv`: 19 filas, incluye `FTr`, `PF` y `STL`.
- `outputs/metrics/eda_estadisticas_descriptivas.csv`: 19 predictores.
- `outputs/metrics/eda_atipicos.csv`: 19 predictores.
- `outputs/metrics/eda_pares_correlacionados.csv`: pares `off_FT/FGA`–`FTr`, `def_FT/FGA`–`PF` y `def_TOV%`–`STL`, que solo existen en la versión de 19.

La carpeta `outputs_corrida1_19vars/` ya existía como respaldo. Se comparó **archivo por archivo** contra `outputs/`:

- 22 archivos en `outputs/`.
- 0 diferencias de SHA256.
- 0 archivos faltantes en el respaldo.
- 0 archivos extra en el respaldo (antes de la nota de identificación descrita abajo).

Por lo tanto, `outputs_corrida1_19vars/` es una copia byte a byte del estado histórico de `outputs/` al momento de la auditoría. **No se modificó ningún archivo de resultados de esa carpeta.**

Después de la comparación se añadió únicamente `outputs_corrida1_19vars/LEEME_RESPALDO.md`, un archivo de texto que identifica la carpeta como histórica. No es un resultado, no reemplaza ningún archivo y no cambia los 22 archivos originales. Si se repite la comparación, ese `LEEME_RESPALDO.md` aparecerá como el único archivo adicional.

## 2. Hashes SHA256 de los CSV de EDA históricos

| Archivo | SHA256 |
|---|---|
| `eda_atipicos.csv` | `48E79E87973D20BA77FA17F6371DAAE4D6A36F3D9B03C3D26AE5F4871D146090` |
| `eda_correlacion_objetivo.csv` | `4CF4C398B46F9230CEC9280BB55A9088B3AE147BD64CF84AE17C77762935A1E3` |
| `eda_estadisticas_descriptivas.csv` | `29068C451D7900DAD5E4539A71AA6736E6C5888D182C7CD85D306E0F1A1FC9C7` |
| `eda_pares_correlacionados.csv` | `85297C7017EDD6CA0361A20177F6A833F9A1D612FB2366590C19040F7AEB8CF5` |

Estos hashes corresponden tanto a `outputs/metrics/` como a `outputs_corrida1_19vars/metrics/` (son idénticos).

## 3. Qué NO debe hacerse

- **No** presentar `outputs/metrics/eda_*.csv` ni `outputs_corrida1_19vars/` como resultados de la corrida actual.
- **No** mezclar las 19 variables con las 16 en una misma tabla o figura.
- **No** borrar `outputs_corrida1_19vars/` ni sobrescribir sus archivos.
- **No** usar los resultados de modelado de 19 variables como si fueran de la corrida de 16. (Cuando se escribió esta nota, la Fase IV de 16 variables aún no se había ejecutado; hoy sus resultados están en `outputs_corrida2_16vars_fase4/`.)

## 4. Dónde está la corrida actual

- Código: `exploracion.py` (16 predictores).
- Resultados: `outputs_corrida2_16vars/`.
- Todos los archivos de la corrida actual llevan el sufijo `_16vars`.
- Documentación: `docs/FASE_III_EDA_16VARS.md`.
- Log final: `outputs_corrida2_16vars/logs/eda_16vars_20261118_130235.log`.

## 5. Diferencia metodológica entre ambas corridas

La corrida de 19 variables incluía:

```text
FOUR_FACTORS (8) + OTHER_FEATURES (11)
OTHER_FEATURES = Age, Pace, 3PAr, 3P%, FT%, AST, STL, BLK, TRB, PF, FTr
```

La corrida actual usa:

```text
FOUR_FACTORS (8) + OTHER_FEATURES (8)
OTHER_FEATURES = Age, Pace, 3PAr, 3P%, FT%, AST, BLK, TRB
```

Se retiraron `FTr`, `PF` y `STL` por su redundancia con variables que se conservan:

- `FTr`–`off_FT/FGA`: r = 0,929 en la corrida de 19.
- `PF`–`def_FT/FGA`: r = 0,893.
- `STL`–`def_TOV%`: r = 0,821.

En la corrida de 16, el único par con |r| ≥ 0,70 es `off_eFG%`–`3P%` (0,709). Esto se documenta en `eda_pares_correlacionados_16vars.csv`.
