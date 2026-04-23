# tests/test_omega_falsification_births.py
from __future__ import annotations

import csv
import math
import os
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple

import pytest


# ============================================================
# CONFIG CI / GITHUB ACTIONS
# ============================================================

REPO_PATH = os.getenv("OMEGA_BIRTHS_REPO", "").strip()
SUBJECT_ID = os.getenv("OMEGA_SUBJECT_ID", "ilver villasmil")

ID_COL = os.getenv("OMEGA_ID_COL", "id")
DATE_COL = os.getenv("OMEGA_DATE_COL", "birth_date")
TIME_COL = os.getenv("OMEGA_TIME_COL", "birth_time")
LAT_COL = os.getenv("OMEGA_LAT_COL", "lat")
LON_COL = os.getenv("OMEGA_LON_COL", "lon")
YEAR_COL = os.getenv("OMEGA_YEAR_COL", "year")

GEOMAG_COL = os.getenv("OMEGA_GEOMAG_COL", "geomag_h_nt")
MOON_COL = os.getenv("OMEGA_MOON_COL", "moon_illum_pct")
PHOTOPERIOD_COL = os.getenv("OMEGA_PHOTOPERIOD_COL", "photoperiod_hours")
TEMP_COL = os.getenv("OMEGA_TEMP_COL", "temp_c")
TOTAL_INTENSITY_COL = os.getenv("OMEGA_TOTAL_INTENSITY_COL", "")

PERMUTATIONS = int(os.getenv("OMEGA_PERMUTATIONS", "10000"))
ALPHA_VAL = float(os.getenv("OMEGA_ALPHA", "0.001"))


def resolve_repo_path() -> str:
    """Busca births.csv en rutas estándar o usa OMEGA_BIRTHS_REPO."""
    candidates: List[str] = []

    if REPO_PATH:
        candidates.append(REPO_PATH)

    candidates.extend(
        [
            "births.csv",
            "data/births.csv",
            "datasets/births.csv",
            "tests/data/births.csv",
            "diagnostics/births.csv",
            "repo/births.csv",
        ]
    )

    for path in candidates:
        if path and os.path.exists(path):
            return path

    raise FileNotFoundError(
        f"No se encontró births.csv. Rutas buscadas: {candidates}\n"
        "1. Define OMEGA_BIRTHS_REPO=tests/data/births.csv en GitHub Actions\n"
        "2. O coloca el archivo en una de: {', '.join(candidates[1:])}"
    )


# ============================================================
# CONSTANTES FIJAS (conectadas al framework Ω)
# ============================================================

E = math.e
PI = math.pi
PHI = (1.0 + math.sqrt(5.0)) / 2.0

# Targets geométricos/cósmicos para máxima coherencia L3-L4
TARGET_LAT_E = 27.0                    # lat * e ≈ 27 (activación cúbica perfecta)
TARGET_LON_LAT = 2.0 * PI + 1.0 / PHI  # lon/|lat| = 2π + 1/φ (ángulo dorado + ciclo)

# Tolerancias para features físicas
TOL_LAT_E_REL = 0.02
TOL_LON_LAT_REL = 0.01
TOL_MOON_ABS = 5.0
TOL_PHOTOPERIOD_ABS = 0.5
TOL_TEMP_ABS = 2.0
TOL_GEOMAG_REL = 0.05

# Targets físicos medidos
TARGET_GEOMAG_H_NT = 27000.0      # Campo horizontal geomagnético ideal
TARGET_TOTAL_INTENSITY_NT = 33500.0
TARGET_MOON_ILLUM = 5.0           # Luna nueva (máxima oscuridad)
TARGET_PHOTOPERIOD = 12.0         # Equinoccio perfecto
TARGET_TEMP = 19.5                # Temperatura fisiológica óptima

WEIGHTS: Dict[str, float] = {
    # Features de alta importancia (peso 1.0) - activan capas principales
    "day_105": 1.0,                    # Día 105 del año (primavera exacta)
    "day_factorization_357": 1.0,      # 105 = 3×5×7 (resonancia perfecta)
    "digit_sum_33": 1.0,               # Número maestro 33
    "hour_3am": 1.0,                   # Pico melatonina
    "lat_e_27": 1.0,                   # Geometría cúbica
    "lon_lat_phi_pi": 1.0,             # Ángulo dorado + ciclo completo
    "geomag_h_27k": 1.0,               # Campo magnético ideal
    
    # Features secundarias (peso 0.5) - moduladores ambientales
    "moon_5pct": 0.5,
    "photoperiod_12h": 0.5,
    "temp_19_5c": 0.5,
}

# Umbrales estadísticos para falsación (extremadamente exigentes)
MIN_PERCENTILE = 0.999          # Top 0.1% del repositorio
MAX_PERMUTATION_P = 0.001       # p-value ≤ 0.1% en permutaciones
MIN_STABILITY = 0.80            # Estabilidad ante ruido ±1%
MIN_REQUIRED_NONZERO_FEATURES = 4  # Mínimo 4 features activas


# ============================================================
# UTILIDADES
# ============================================================

def clamp01(x: float) -> float:
    """Clampa valor al rango [0,1] para normalización de features."""
    return max(0.0, min(1.0, x))


def relative_closeness(value: float, target: float, tol_rel: float) -> float:
    """Cercanía relativa normalizada [0,1]."""
    if target == 0:
        return 1.0 if value == 0 else 0.0
    rel_err = abs(value - target) / abs(target)
    return clamp01(1.0 - rel_err / tol_rel)


def absolute_closeness(value: float, target: float, tol_abs: float) -> float:
    """Cercanía absoluta normalizada [0,1]."""
    abs_err = abs(value - target)
    return clamp01(1.0 - abs_err / tol_abs)


def digit_sum_from_date_parts(year: int, month: int, day: int) -> int:
    """Suma dígitos de fecha en formato DDMMYYYY."""
    s = f"{day:02d}{month:02d}{year:04d}"
    return sum(int(ch) for ch in s)


def is_product_3_5_7(n: int) -> bool:
    """Verifica si n = 3×5×7 = 105 (resonancia perfecta)."""
    return n == 3 * 5 * 7


def day_of_year(dt: date) -> int:
    """Día del año (1-365/366)."""
    return dt.timetuple().tm_yday


def parse_date(v: str) -> date:
    """Parse flexible de fechas."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(v.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Fecha no válida: {v}")


def parse_time(v: str) -> time:
    """Parse flexible de horas."""
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(v.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Hora no válida: {v}")


def safe_float(v: Any) -> Optional[float]:
    """Convierte a float seguro, None si inválido."""
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def percentile_rank(values: List[float], x: float) -> float:
    """Percentil del valor x en la lista values."""
    if not values:
        return float("nan")
    le = sum(1 for v in values if v <= x)
    return le / len(values)


def utc_shift_hour(local_hour: int, offset_hours: int = 4) -> int:
    """Ajusta hora local a UTC (+4h)."""
    return (local_hour + offset_hours) % 24


# ============================================================
# MODELOS DE DATOS
# ============================================================

@dataclass(frozen=True)
class SubjectRecord:
    """Registro completo de nacimiento con datos ambientales."""
    row_id: str
    birth_date: date
    birth_time: time
    lat: float
    lon: float
    year: int
    geomag_h_nt: Optional[float] = None
    moon_illum_pct: Optional[float] = None
    photoperiod_hours: Optional[float] = None
    temp_c: Optional[float] = None
    total_intensity_nt: Optional[float] = None


@dataclass(frozen=True)
class FeatureScores:
    """Puntuaciones normalizadas [0,1] de cada feature Ω."""
    day_105: float
    day_factorization_357: float
    digit_sum_33: float
    hour_3am: float
    lat_e_27: float
    lon_lat_phi_pi: float
    geomag_h_27k: float
    moon_5pct: float
    photoperiod_12h: float
    temp_19_5c: float

    def weighted_score(self) -> float:
        """Score ponderado total [0,1]. Ignora NaN."""
        num = 0.0
        den = 0.0
        for k, w in WEIGHTS.items():
            v = getattr(self, k)
            if math.isnan(v):
                continue
            num += w * v
            den += w
        return num / den if den > 0 else 0.0

    def nonzero_count(self) -> int:
        """Número de features activas (v > 0 y no NaN)."""
        c = 0
        for k in WEIGHTS:
            v = getattr(self, k)
            if not math.isnan(v) and v > 0:
                c += 1
        return c


@dataclass(frozen=True)
class FalsificationResult:
    """Resultado completo de falsación estadística."""
    subject_id: str
    subject_score: float
    subject_features: Dict[str, float]
    percentile_vs_repo: float
    permutation_p: float
    stability: float
    nonzero_features: int
    falsified: bool
    fail_reasons: List[str]
    repo_n: int


# ============================================================
# CORE DE CÁLCULO
# ============================================================

def compute_feature_scores(s: SubjectRecord) -> FeatureScores:
    """Calcula todas las features Ω normalizadas [0,1] del sujeto."""
    # Features temporales exactas (binarias)
    doy = day_of_year(s.birth_date)
    ds = digit_sum_from_date_parts(s.year, s.birth_date.month, s.birth_date.day)
    hour_val = s.birth_time.hour

    # Features geométricas continuas
    lat_e = s.lat * E
    lon_lat = abs(s.lon) / s.lat if s.lat != 0 else float("inf")

    # Features ambientales (opcionales)
    geomag_score = float("nan")
    if s.geomag_h_nt is not None:
        geomag_score = relative_closeness(
            s.geomag_h_nt, TARGET_GEOMAG_H_NT, TOL_GEOMAG_REL
        )

    moon_score = float("nan")
    if s.moon_illum_pct is not None:
        moon_score = absolute_closeness(s.moon_illum_pct, TARGET_MOON_ILLUM, TOL_MOON_ABS)

    photoperiod_score = float("nan")
    if s.photoperiod_hours is not None:
        photoperiod_score = absolute_closeness(
            s.photoperiod_hours, TARGET_PHOTOPERIOD, TOL_PHOTOPERIOD_ABS
        )

    temp_score = float("nan")
    if s.temp_c is not None:
        temp_score = absolute_closeness(s.temp_c, TARGET_TEMP, TOL_TEMP_ABS)

    return FeatureScores(
        day_105=1.0 if doy == 105 else 0.0,
        day_factorization_357=1.0 if is_product_3_5_7(doy) else 0.0,
        digit_sum_33=1.0 if ds == 33 else 0.0,
        hour_3am=1.0 if hour_val == 3 else 0.0,
        lat_e_27=relative_closeness(lat_e, TARGET_LAT_E, TOL_LAT_E_REL),
        lon_lat_phi_pi=relative_closeness(lon_lat, TARGET_LON_LAT, TOL_LON_LAT_REL),
        geomag_h_27k=geomag_score,
        moon_5pct=moon_score,
        photoperiod_12h=photoperiod_score,
        temp_19_5c=temp_score,
    )


def stability_test(s: SubjectRecord, base_score: float) -> Dict[str, Any]:
    """Prueba robustez del score ante ruido (±1% lat/lon, +4h hora)."""
    variants: List[float] = []

    # Variante 1: Shift temporal UTC (+4h)
    shifted = SubjectRecord(
        row_id=s.row_id,
        birth_date=s.birth_date,
        birth_time=time(
            hour=utc_shift_hour(s.birth_time.hour, 4),
            minute=s.birth_time.minute,
            second=s.birth_time.second,
        ),
        lat=s.lat,
        lon=s.lon,
        year=s.year,
        geomag_h_nt=s.geomag_h_nt,
        moon_illum_pct=s.moon_illum_pct,
        photoperiod_hours=s.photoperiod_hours,
        temp_c=s.temp_c,
        total_intensity_nt=s.total_intensity_nt,
    )
    variants.append(compute_feature_scores(shifted).weighted_score())

    # Variantes 2-5: Ruido espacial ±1%
    deltas = [(-0.01, 0.0), (0.01, 0.0), (0.0, -0.01), (0.0, 0.01)]
    for dlat, dlon in deltas:
        vv = SubjectRecord(
            row_id=s.row_id,
            birth_date=s.birth_date,
            birth_time=s.birth_time,
            lat=s.lat + dlat,
            lon=s.lon + dlon,
            year=s.year,
            geomag_h_nt=s.geomag_h_nt,
            moon_illum_pct=s.moon_illum_pct,
            photoperiod_hours=s.photoperiod_hours,
            temp_c=s.temp_c,
            total_intensity_nt=s.total_intensity_nt,
        )
        variants.append(compute_feature_scores(vv).weighted_score())

    # Estabilidad = 1 - caída_promedio / score_base
    drops = [abs(v - base_score) for v in variants]
    mean_drop = statistics.mean(drops) if drops else 1.0
    stability = clamp01(1.0 - mean_drop / max(base_score, 1e-9))

    return {
        "base_score": base_score,
        "mean_drop": mean_drop,
        "stability": stability,
        "variant_scores": variants,
    }


def load_repo(
    path: str,
    id_col: str,
    date_col: str,
    time_col: str,
    lat_col: str,
    lon_col: str,
    year_col: str,
    geomag_col: str,
    moon_col: str,
    photoperiod_col: str,
    temp_col: str,
    total_intensity_col: str,
) -> List[SubjectRecord]:
    """Carga y parsea el archivo CSV de nacimientos."""
    records = []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rec = SubjectRecord(
                    row_id=row[id_col],
                    birth_date=parse_date(row[date_col]),
                    birth_time=parse_time(row[time_col]),
                    lat=float(row[lat_col]),
                    lon=float(row[lon_col]),
                    year=int(row[year_col]),
                    geomag_h_nt=safe_float(row.get(geomag_col)),
                    moon_illum_pct=safe_float(row.get(moon_col)),
                    photoperiod_hours=safe_float(row.get(photoperiod_col)),
                    temp_c=safe_float(row.get(temp_col)),
                    total_intensity_nt=safe_float(row.get(total_intensity_col)),
                )
                records.append(rec)
            except (ValueError, KeyError):
                continue
    return records
