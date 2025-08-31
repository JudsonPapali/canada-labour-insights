
# backend/data_pipeline.py
import io
import os
import zipfile
import time
import requests
import pandas as pd
from typing import Tuple

TABLE_PID = "14100287"  # Labour force characteristics by province, monthly, seasonally adjusted
CSV_ZIP_EN = f"https://www150.statcan.gc.ca/n1/en/tbl/csv/{TABLE_PID}-eng.zip"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_PATH = os.path.join(CACHE_DIR, f"{TABLE_PID}.csv")
CACHE_MAX_AGE_SEC = 7 * 24 * 3600  # 7 dias

# Colunas esperadas (nomes podem variar levemente ao longo do tempo). Faremos matching flexível.
COL_REF_DATE = "REF_DATE"
COL_GEO = "GEO"
COL_CHAR = "Labour force characteristics"
COL_SEX = "Sex"
COL_AGE = "Age group"
COL_ADJ = "Seasonal adjustment"
COL_VALUE = "VALUE"

# Rótulos-alvo
LABEL_UNEMPLOYMENT = "Unemployment rate"
LABEL_BOTH_SEXES = "Both sexes"
LABEL_15PLUS = "15 years and over"
LABEL_SA = "Seasonally adjusted"

PROVINCES = [
    "Canada", "Newfoundland and Labrador", "Prince Edward Island", "Nova Scotia",
    "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan", "Alberta",
    "British Columbia", "Yukon", "Northwest Territories", "Nunavut"
]

os.makedirs(CACHE_DIR, exist_ok=True)


def _download_and_extract_csv() -> pd.DataFrame:
    resp = requests.get(CSV_ZIP_EN, timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        # Procura o primeiro CSV do pacote
        name = next((n for n in zf.namelist() if n.lower().endswith('.csv')), None)
        if not name:
            raise RuntimeError("CSV não encontrado no ZIP do StatCan")
        with zf.open(name) as f:
            df = pd.read_csv(f)
    return df


def _columns_best_guess(df: pd.DataFrame) -> Tuple[str, str, str, str, str, str]:
    # Mapeia colunas por aproximação, caso nomes mudem
    cols = list(df.columns)
    def find(name):
        # busca por igual ou contém (case-insensitive)
        for c in cols:
            if c.strip().lower() == name.lower():
                return c
        for c in cols:
            if name.lower() in c.strip().lower():
                return c
        raise KeyError(f"Coluna não encontrada: {name}")

    return (
        find(COL_REF_DATE),
        find(COL_GEO),
        find(COL_CHAR),
        find(COL_SEX),
        find(COL_AGE),
        find(COL_VALUE),
    )


def ensure_cached_csv() -> pd.DataFrame:
    need_refresh = True
    if os.path.exists(CACHE_PATH):
        age = time.time() - os.path.getmtime(CACHE_PATH)
        if age < CACHE_MAX_AGE_SEC:
            need_refresh = False
    if need_refresh:
        df = _download_and_extract_csv()
        df.to_csv(CACHE_PATH, index=False)
    else:
        df = pd.read_csv(CACHE_PATH)
    return df


def unemployment_timeseries(geo: str, latest_n: int = 24) -> pd.DataFrame:
    if geo not in PROVINCES:
        raise ValueError(f"Região inválida. Use um de: {', '.join(PROVINCES)}")

    df = ensure_cached_csv()
    ref, geo_col, char, sex, age, val = _columns_best_guess(df)

    # Filtro principal
    mask = (
        (df[char] == LABEL_UNEMPLOYMENT)
        & (df[sex] == LABEL_BOTH_SEXES)
        & (df[age] == LABEL_15PLUS)
        & (df[geo_col] == geo)
    )

    sub = df.loc[mask, [ref, val]].copy()
    # Alguns CSVs usam vírgula como decimal em locale — garantir numérico
    sub[val] = pd.to_numeric(sub[val], errors='coerce')
    sub = sub.dropna().sort_values(by=ref)

    if latest_n and latest_n > 0:
        sub = sub.tail(latest_n)

    # Normaliza data como AAAA-MM
    sub[ref] = pd.to_datetime(sub[ref], errors='coerce').dt.strftime('%Y-%m')

    return sub.reset_index(drop=True)


def list_regions():
    return PROVINCES
