"""
Pruebas automáticas del proyecto (sin dependencias externas).

Ejecutar desde la raíz del proyecto:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v

Cubren:
  1. Integridad del dataset procesado.
  2. Contrato de los 16 predictores.
  3. Cálculo de las variables relativas.
  4. Coherencia de los artefactos de Fase IV.
  5. Que el pipeline de modelado entrene y devuelva probabilidades válidas.
"""
from __future__ import annotations

import json
import sys
import unittest
from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exploracion import FEATURES, FOUR_FACTORS, OTHER_FEATURES, TARGET, add_relative_features  # noqa: E402

DATA_FILE = ROOT / "data" / "processed" / "nba_teams_clean.csv"
FASE4 = ROOT / "outputs_corrida2_16vars_fase4"
EXPECTED_SHA256 = "c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9"

# El repositorio público no incluye datos. Las pruebas que los necesitan se omiten
# con un mensaje explícito en lugar de fallar.
DATA_AVAILABLE = DATA_FILE.is_file()
requires_data = unittest.skipUnless(
    DATA_AVAILABLE,
    "Requiere data/processed/nba_teams_clean.csv; ejecuta scraping.py y limpieza.py",
)

PROHIBIDOS = {
    "W", "L", "PW", "PL", "MOV", "SOS", "SRS", "NRtg",
    "win_pct", "Rk", "ORtg", "DRtg", "Attend.", "Attend./G",
}


def sha256_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@requires_data
class TestDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATA_FILE)

    def test_archivo_existe(self):
        self.assertTrue(DATA_FILE.is_file(), f"No existe {DATA_FILE}")

    def test_hash_esperado(self):
        """El dataset no debe cambiar entre corridas documentadas."""
        self.assertEqual(sha256_file(DATA_FILE), EXPECTED_SHA256)

    def test_dimensiones(self):
        self.assertEqual(self.df.shape, (805, 52))

    def test_temporadas(self):
        self.assertEqual(self.df["season"].min(), 2000)
        self.assertEqual(self.df["season"].max(), 2026)
        self.assertEqual(self.df["season"].nunique(), 27)

    def test_clave_unica(self):
        self.assertFalse(
            self.df.duplicated(subset=["season", "Team"]).any(),
            "Hay duplicados en (season, Team)",
        )
        self.assertFalse(self.df.duplicated().any(), "Hay filas duplicadas exactas")

    def test_objetivo_binario(self):
        self.assertEqual(set(self.df[TARGET].unique()), {0, 1})
        self.assertEqual(int(self.df[TARGET].sum()), 432)
        self.assertEqual(int((self.df[TARGET] == 0).sum()), 373)

    def test_sin_nulos_en_predictores(self):
        self.assertTrue(self.df[FEATURES].notna().all().all())
        self.assertTrue(np.isfinite(self.df[FEATURES].to_numpy()).all())

    def test_nulos_documentados(self):
        """Solo Attend. y Attend./G tienen nulos, y están excluidas."""
        con_nulos = set(self.df.columns[self.df.isna().any()])
        self.assertEqual(con_nulos, {"Attend.", "Attend./G"})
        self.assertEqual(int(self.df["Attend."].isna().sum()), 4)


class TestPredictores(unittest.TestCase):
    def test_cantidad(self):
        self.assertEqual(len(FEATURES), 16)
        self.assertEqual(len(FOUR_FACTORS), 8)
        self.assertEqual(len(OTHER_FEATURES), 8)

    def test_sin_duplicados(self):
        self.assertEqual(len(FEATURES), len(set(FEATURES)))

    def test_sin_prohibidos(self):
        interseccion = set(FEATURES) & PROHIBIDOS
        self.assertEqual(interseccion, set(), f"Predictores prohibidos: {interseccion}")

    def test_objetivo_no_es_predictor(self):
        self.assertNotIn(TARGET, FEATURES)


@requires_data
class TestVariablesRelativas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATA_FILE)
        cls.rel = add_relative_features(cls.df, FEATURES)
        cls.cols_rel = [f"{c}_rel" for c in FEATURES]

    def test_columnas_creadas(self):
        for col in self.cols_rel:
            self.assertIn(col, self.rel.columns)

    def test_media_por_temporada_es_cero(self):
        """x_rel = x - media de su temporada => media ~ 0 en cada temporada."""
        medias = self.rel.groupby("season")[self.cols_rel].mean().abs()
        self.assertLess(float(medias.to_numpy().max()), 1e-9)

    def test_calculo_manual(self):
        col = "3PAr"
        temporada = 2026
        sub = self.df[self.df["season"] == temporada]
        esperado = sub[col] - sub[col].mean()
        obtenido = self.rel.loc[sub.index, f"{col}_rel"]
        np.testing.assert_allclose(obtenido.to_numpy(), esperado.to_numpy(), atol=1e-12)

    def test_no_altera_original(self):
        self.assertNotIn("3PAr_rel", self.df.columns)


class TestArtefactosFaseIV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resumen = json.loads(
            (FASE4 / "metrics" / "modelado_resumen_16vars.json").read_text(encoding="utf-8")
        )

    def test_resumen_existe_y_es_16_vars(self):
        self.assertEqual(self.resumen["n_features"], 16)
        self.assertEqual(self.resumen["n_rows"], 805)
        self.assertEqual(self.resumen["input_sha256"], EXPECTED_SHA256)

    def test_dos_protocolos(self):
        self.assertEqual(set(self.resumen["protocolos"]), {"temporal", "estratificado"})

    def test_metricas_en_rango(self):
        for protocolo in self.resumen["protocolos"].values():
            for clave in ("accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc", "brier"):
                valor = protocolo["test_umbral"][clave]
                self.assertGreaterEqual(valor, 0.0, f"{clave} fuera de rango")
                self.assertLessEqual(valor, 1.0, f"{clave} fuera de rango")

    def test_supera_linea_base(self):
        for protocolo in self.resumen["protocolos"].values():
            self.assertGreater(protocolo["test_umbral"]["roc_auc"], 0.5)
            self.assertGreater(protocolo["test_umbral"]["f1"], 0.6963)  # F1 trivial

    def test_figuras_esperadas(self):
        figuras = {p.name for p in (FASE4 / "figures").glob("*.png")}
        for protocolo in ("temporal", "estratificado"):
            for tipo in ("matriz_confusion", "curva_roc", "curva_pr", "calibracion", "importancia"):
                self.assertIn(f"modelado_{tipo}_{protocolo}_16vars.png", figuras)

    def test_historial_intacto(self):
        """La corrida histórica de 19 variables debe seguir presente."""
        self.assertTrue((ROOT / "outputs_corrida1_19vars").is_dir())
        self.assertTrue((ROOT / "outputs" / "metrics" / "modelado_resumen.json").is_file())


@requires_data
class TestPipelineEntrena(unittest.TestCase):
    def test_logistica_con_cv_agrupada(self):
        """Prueba rápida: el pipeline corre y devuelve probabilidades válidas."""
        df = pd.read_csv(DATA_FILE)
        df = add_relative_features(df, FEATURES)
        X = df[[f"{c}_rel" for c in FEATURES]].head(200)
        y = df[TARGET].astype(int).head(200)
        grupos = df["season"].head(200)

        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ])
        cv = StratifiedGroupKFold(n_splits=3)
        scores = cross_val_score(pipe, X, y, groups=grupos, cv=cv, scoring="accuracy")
        self.assertEqual(len(scores), 3)
        self.assertTrue(np.isfinite(scores).all())
        self.assertTrue(((scores >= 0) & (scores <= 1)).all())

        pipe.fit(X, y)
        proba = pipe.predict_proba(X)[:, 1]
        self.assertTrue(((proba >= 0) & (proba <= 1)).all())


if __name__ == "__main__":
    unittest.main(verbosity=2)
