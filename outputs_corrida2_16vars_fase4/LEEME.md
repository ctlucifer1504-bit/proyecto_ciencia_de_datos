# Fase IV — Modelado con 16 predictores

**Run ID:** `corrida2_16vars_fase4`
**Fecha:** 2026-11-18, 13:46:13–13:47:11 (hora local)
**Entrada:** `data/processed/nba_teams_clean.csv`
**SHA256 de entrada:** `c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9`
**Script:** `modelado.py`
**Informe:** `docs/FASE_IV_MODELADO_16VARS.md`

Esta carpeta contiene **solo** la corrida de 16 predictores. No mezcla resultados con la
corrida histórica de 19 variables.

## Contenido

| Carpeta | Contenido |
|---|---|
| `figures/` | 10 figuras: matriz de confusión, ROC, precision-recall, calibración e importancia por permutación, para los protocolos `temporal` y `estratificado`. |
| `metrics/` | 23 archivos: métricas de CV, test, grillas, coeficientes, VIF, sensibilidad, predicciones, resumen JSON/TXT y manifiesto. |
| `logs/` | 3 logs del script y 3 logs de consola. |

## Protocolos

1. **Temporal (principal):** train 2000–2019 (595 filas), test 2020–2026 (210 filas),
   `StratifiedGroupKFold(5)` agrupado por temporada.
2. **Estratificado (secundario):** 80/20 con `StratifiedKFold(5)`; no se usa para elegir
   el modelo final.

## Resultado principal

Regresión logística (`C=0.1`), umbral 0,46, test temporal:

| Métrica | Valor |
|---|---:|
| Accuracy | 0,862 |
| Precision | 0,822 |
| Recall | 0,946 |
| F1 | 0,880 |
| ROC-AUC | 0,942 |
| PR-AUC | 0,947 |
| Brier | 0,097 |

`GridSearchCV` mejoró la validación cruzada (+0,004 en F1) pero **no mejoró el test**.
Se reporta sin inflar el resultado.

## Reproducir

```powershell
& .\.venv\Scripts\python.exe modelado.py
```

> **Advertencia:** volver a ejecutar el script **sobrescribe** los archivos de esta carpeta
> con una nueva marca de tiempo. No afecta a `outputs/` ni a `outputs_corrida1_19vars/`.

## Historial

Los resultados de 19 variables están en `outputs/` y respaldados en
`outputs_corrida1_19vars/`. No deben presentarse como resultados actuales.
