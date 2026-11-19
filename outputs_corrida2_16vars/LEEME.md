# Corrida actual de Fase III — 16 predictores

Esta carpeta contiene **solo** los resultados de la corrida actual de EDA con **16 predictores**. No mezclar con `../outputs/` ni con `../outputs_corrida1_19vars/`, que son la corrida histórica de 19 variables.

## Ejecución

Desde la raíz del proyecto:

```powershell
& .\.venv\Scripts\python.exe exploracion.py
```

- Fecha/hora: 2026-11-18, 13:02:35–13:02:44 (hora local).
- Python 3.15.2; pandas 3.1.1; numpy 2.5.5; matplotlib 3.11.2; scikit-learn 1.9.1 (no usado).
- Entrada: `../data/processed/nba_teams_clean.csv`.
- SHA256 de la entrada: `c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9`.
- Código de salida: 0.
- Duración: 11,98 s.

## Contenido

- `figures/`: 11 figuras PNG; todas llevan `_16vars` en el nombre.
- `metrics/`: 14 tablas CSV, un resumen legible (`eda_resumen_16vars.txt`) y metadatos (`eda_resumen_ejecucion_16vars.json`).
- `logs/`: log del script y capturas de consola. La corrida válida es la de **13:02**:
  - `logs/eda_16vars_20261118_130235.log`
  - `logs/consola_eda_16vars_20261118_130233.txt`

## Predictores (16)

```text
off_eFG%, off_TOV%, off_ORB%, off_FT/FGA,
def_eFG%, def_TOV%, def_DRB%, def_FT/FGA,
Age, Pace, 3PAr, 3P%, FT%, AST, BLK, TRB
```

Variable objetivo: `playoffs` (0/1).

## Documentación

- Informe completo: `../docs/FASE_III_EDA_16VARS.md`.
- Auditoría del respaldo de 19 variables: `../docs/RESPALDO_19VARS.md`.

## Advertencia

No se ejecutó la Fase IV. Los archivos `modelado_*` de `../outputs/` son de la corrida histórica de 19 variables y no deben presentarse como resultados de esta corrida.
