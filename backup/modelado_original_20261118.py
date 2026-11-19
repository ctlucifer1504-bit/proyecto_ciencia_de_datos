"""
FASE IV - Machine Learning y optimizacion
Entrada : data/processed/nba_teams_clean.csv  (Fase II)
Salida  : outputs/metrics/modelado_*.csv|json   y   outputs/figures/08_*.png, 09_*.png

Problema: CLASIFICACION binaria -> el equipo clasifica a playoffs (1) o no (0).

Controles contra fuga de datos (data leakage):
  - Predictores = estadisticas de juego relativas a la temporada (ver exploracion.py).
    Se excluyen W, L, MOV, SRS, NRtg, win_pct, Rk (revelan el resultado) y, en el
    analisis principal, ORtg/DRtg (casi equivalen al margen de puntos).
  - train/test se separan ANTES de ajustar nada; el test no se usa para elegir.
  - Imputacion y escalado viven dentro del Pipeline: se aprenden solo con el
    entrenamiento de cada fold.
  - Modelo base y GridSearchCV usan EXACTAMENTE los mismos folds (mismo objeto cv).

Uso:  pip install scikit-learn
      python modelado.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import (GridSearchCV, StratifiedKFold, cross_validate,
                                     train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from exploracion import FEATURES, TARGET, add_relative_features

# --------------------------------------------------------------------------
# Configuracion
# --------------------------------------------------------------------------
DATA_FILE = Path("data/processed/nba_teams_clean.csv")
FIG_DIR = Path("outputs/figures")
METRICS_DIR = Path("outputs/metrics")

RANDOM_STATE = 42
TEST_SIZE = 0.20
N_FOLDS = 5                      # la guia exige minimo 5
TEMPORAL_CUTOFF = 2019           # robustez: entrenar <= 2019, probar > 2019

SCORING = {"accuracy": "accuracy", "precision": "precision", "recall": "recall",
           "f1": "f1", "roc_auc": "roc_auc"}
REFIT = "accuracy"               # metrica con la que GridSearchCV elige (clases equilibradas)

# Modelos candidatos y sus grillas (prefijo clf__ = paso del Pipeline)
MODELS = {
    "LogisticRegression": (
        LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        {"clf__C": [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]},
    ),
    "RandomForest": (
        RandomForestClassifier(random_state=RANDOM_STATE),
        {"clf__n_estimators": [200, 400], "clf__max_depth": [3, 5, 8, None],
         "clf__min_samples_leaf": [1, 3, 5], "clf__max_features": ["sqrt", 0.5]},
    ),
}


def make_pipeline(estimator) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", clone(estimator)),
    ])


def evaluate(model, X, y) -> dict:
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1]
    return {"accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred),
            "recall": recall_score(y, pred), "f1": f1_score(y, pred),
            "roc_auc": roc_auc_score(y, proba)}


def cv_summary(scores: dict) -> dict:
    """Media y desviacion entre folds de cada metrica."""
    out = {}
    for name in SCORING:
        vals = scores[f"test_{name}"]
        out[f"cv_{name}"] = float(np.mean(vals))
        out[f"cv_{name}_std"] = float(np.std(vals))
    return out


def run_grid(name, estimator, grid, X, y, cv) -> GridSearchCV:
    search = GridSearchCV(make_pipeline(estimator), grid, scoring=SCORING, refit=REFIT,
                          cv=cv, n_jobs=-1)
    t0 = time.time()
    search.fit(X, y)
    n_combos = len(search.cv_results_["params"])
    print(f"  {name}: {n_combos} combinaciones x {N_FOLDS} folds = {n_combos * N_FOLDS} ajustes "
          f"({time.time() - t0:.0f} s)")
    pd.DataFrame(search.cv_results_).to_csv(METRICS_DIR / f"modelado_gridsearch_{name}.csv", index=False)
    return search


def best_row_summary(search: GridSearchCV) -> dict:
    i = search.best_index_
    res = search.cv_results_
    return {f"cv_{m}": float(res[f"mean_test_{m}"][i]) for m in SCORING} | {
        f"cv_{m}_std": float(res[f"std_test_{m}"][i]) for m in SCORING}


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"scikit-learn {sklearn.__version__} | pandas {pd.__version__} | numpy {np.__version__}")

    # ---- Datos ------------------------------------------------------------
    df = add_relative_features(pd.read_csv(DATA_FILE), FEATURES)
    feature_cols = [f"{c}_rel" for c in FEATURES]
    X, y = df[feature_cols], df[TARGET].astype(int)
    print(f"Filas: {len(df)} | predictores: {len(feature_cols)} | clase positiva: {y.mean():.1%}")

    # ---- Particion train/test (antes de cualquier ajuste) ----------------
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df.index, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE)
    print(f"Train: {len(X_train)} | Test: {len(X_test)} (estratificado, random_state={RANDOM_STATE})")

    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    # ---- Linea base trivial ----------------------------------------------
    print("\n[1] Linea base trivial (siempre predice la clase mayoritaria)")
    dummy = DummyClassifier(strategy="most_frequent")
    dummy_cv = cross_validate(make_pipeline(dummy), X_train, y_train, cv=cv,
                              scoring={"accuracy": "accuracy"})
    dummy_acc = float(np.mean(dummy_cv["test_accuracy"]))
    print(f"  accuracy CV = {dummy_acc:.3f}  (cualquier modelo debe superar esto)")

    # ---- Modelo base vs GridSearchCV -------------------------------------
    print("\n[2] Modelo base (hiperparametros por defecto) vs GridSearchCV, mismos folds")
    rows, searches = [], {}
    for name, (estimator, grid) in MODELS.items():
        base_scores = cross_validate(make_pipeline(estimator), X_train, y_train, cv=cv, scoring=SCORING)
        base = cv_summary(base_scores)
        search = run_grid(name, estimator, grid, X_train, y_train, cv)
        tuned = best_row_summary(search)
        searches[name] = search
        for stage, metrics, params in (("base", base, "defecto"), ("optimizado", tuned, search.best_params_)):
            rows.append({"modelo": name, "etapa": stage, "parametros": str(params), **metrics})
        delta = tuned["cv_accuracy"] - base["cv_accuracy"]
        within = abs(delta) <= base["cv_accuracy_std"]
        print(f"    base  accuracy CV = {base['cv_accuracy']:.3f} +- {base['cv_accuracy_std']:.3f}")
        print(f"    optim accuracy CV = {tuned['cv_accuracy']:.3f} +- {tuned['cv_accuracy_std']:.3f} "
              f"| mejor: {search.best_params_}")
        print(f"    diferencia = {delta:+.3f} ({'dentro' if within else 'fuera'} de 1 desviacion entre folds)")
    results = pd.DataFrame(rows)
    results.to_csv(METRICS_DIR / "modelado_cv_base_vs_optimizado.csv", index=False)

    # ---- Seleccion del modelo final (solo con CV) ------------------------
    tuned_only = results[results["etapa"] == "optimizado"].set_index("modelo")
    final_name = tuned_only["cv_accuracy"].idxmax()
    final_model = searches[final_name].best_estimator_
    print(f"\n[3] Modelo final elegido por CV (sin mirar test): {final_name}")
    print("    Nota: best_score_ es algo optimista (se eligio el maximo entre muchas combinaciones);")
    print("    la estimacion honesta es la evaluacion en test.")

    # ---- Evaluacion en test (una sola vez, tras elegir) ------------------
    print("\n[4] Evaluacion en TEST (decisiones ya tomadas; no se usa para elegir nada)")
    base_same_family = make_pipeline(MODELS[final_name][0]).fit(X_train, y_train)
    dummy_fit = make_pipeline(dummy).fit(X_train, y_train)
    test_rows = [
        {"modelo": "Linea base trivial", **{k: v for k, v in evaluate(dummy_fit, X_test, y_test).items()
                                          if k != "roc_auc"}},
        {"modelo": f"{final_name} (base)", **evaluate(base_same_family, X_test, y_test)},
        {"modelo": f"{final_name} (optimizado)", **evaluate(final_model, X_test, y_test)},
    ]
    test_df = pd.DataFrame(test_rows)
    test_df.to_csv(METRICS_DIR / "modelado_test.csv", index=False)
    print(test_df.round(3).to_string(index=False))

    disp = ConfusionMatrixDisplay.from_estimator(
        final_model, X_test, y_test, display_labels=["No clasifico", "Clasifico"], cmap="Blues")
    disp.ax_.set_title(f"Matriz de confusion en test: {final_name} optimizado")
    disp.ax_.set_xlabel("Prediccion del modelo")
    disp.ax_.set_ylabel("Resultado real")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "08_matriz_confusion.png", dpi=150)
    plt.close()

    # ---- Importancia de variables (descriptiva) --------------------------
    perm = permutation_importance(final_model, X_test, y_test, n_repeats=20,
                                  random_state=RANDOM_STATE, scoring="accuracy")
    imp = pd.DataFrame({"variable": [c.replace("_rel", "") for c in feature_cols],
                        "caida_accuracy": perm.importances_mean,
                        "desv": perm.importances_std}).sort_values("caida_accuracy", ascending=False)
    imp.to_csv(METRICS_DIR / "modelado_importancia_variables.csv", index=False)
    top = imp.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh(top["variable"], top["caida_accuracy"], xerr=top["desv"], color="#1f6fb2")
    ax.set_title("Importancia por permutacion (test): que variables sostienen la prediccion")
    ax.set_xlabel("Caida del accuracy al desordenar la variable")
    ax.set_ylabel("Predictor")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "09_importancia_variables.png", dpi=150)
    plt.close()
    print("\n[5] Variables mas importantes (permutacion, test):")
    print(imp.head(8).round(4).to_string(index=False))
    print("    Importancia NO implica causalidad: describe asociacion en estos datos.")

    # ---- Sensibilidad: agregar ORtg y DRtg (solo CV) ---------------------
    print("\n[6] Sensibilidad: que pasa si se agregan ORtg y DRtg (casi equivalen al margen de puntos)")
    df_s = add_relative_features(df, ["ORtg", "DRtg"])
    cols_s = feature_cols + ["ORtg_rel", "DRtg_rel"]
    est, grid = MODELS[final_name]
    search_s = run_grid(f"{final_name}_con_ratings", est, grid, df_s.loc[idx_train, cols_s], y_train, cv)
    print(f"    accuracy CV sin ratings = {tuned_only.loc[final_name, 'cv_accuracy']:.3f} | "
          f"con ratings = {search_s.best_score_:.3f}")
    print("    Solo informativo: el analisis principal NO usa ratings por su cercania al resultado.")

    # ---- Robustez temporal ------------------------------------------------
    print(f"\n[7] Robustez temporal: entrenar con temporadas <= {TEMPORAL_CUTOFF}, probar con las posteriores")
    early, late = df["season"] <= TEMPORAL_CUTOFF, df["season"] > TEMPORAL_CUTOFF
    temporal = clone(final_model).fit(X[early], y[early])
    temporal_metrics = evaluate(temporal, X[late], y[late])
    print(f"    train={early.sum()} | test={late.sum()} | " +
          " | ".join(f"{k}={v:.3f}" for k, v in temporal_metrics.items()))
    print("    Particion distinta a la del paso [4]: no son directamente comparables.")

    # ---- Guardado ---------------------------------------------------------
    summary = {"modelo_final": final_name, "mejores_parametros": searches[final_name].best_params_,
               "n_train": len(X_train), "n_test": len(X_test), "n_folds": N_FOLDS,
               "random_state": RANDOM_STATE, "accuracy_linea_base_cv": dummy_acc,
               "robustez_temporal": temporal_metrics,
               "versiones": {"sklearn": sklearn.__version__, "pandas": pd.__version__}}
    (METRICS_DIR / "modelado_resumen.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"\nResultados guardados en {METRICS_DIR}/ y figuras en {FIG_DIR}/")


if __name__ == "__main__":
    main()
