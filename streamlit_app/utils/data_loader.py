import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"

SAMPLE_NOTICE = (
    "**Note:** This dashboard is loaded with sample data that matches the "
    "expected output schema. Replace the CSV files in `streamlit_app/data/` "
    "with the real outputs from the analysis notebooks."
)


@st.cache_data
def load_file1() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "file1.csv")


@st.cache_data
def load_file2() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "file2.csv")


@st.cache_data
def load_file3() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "file3.csv")


@st.cache_data
def load_emerging() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "emerging_markets_ranking.csv")
    df["province_code"] = df["province_code"].astype(str).str.zfill(2)
    df["cagr_pct"] = (df["cagr"] * 100).round(1)
    return df


@st.cache_data
def load_forecast() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ev_forecast.csv", parse_dates=["date"])


@st.cache_data
def load_provinces() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(DATA_DIR / "spain_provinces.geojson")
    gdf["cod_prov"] = gdf["cod_prov"].astype(str).str.zfill(2)
    return gdf


@st.cache_data
def load_ev_type_mix() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "ev_type_mix.csv")


@st.cache_data
def load_provinces_geojson_str() -> str:
    with open(DATA_DIR / "spain_provinces.geojson", encoding="utf-8") as f:
        return f.read()


# TEN-T corridor waypoints [lon, lat] — hardcoded from MITMA interurban network
CORRIDORS: dict[str, list[list[float]]] = {
    "A-1":  [[-3.70, 40.42], [-3.68, 41.67], [-3.70, 42.35], [-2.94, 42.68], [-2.67, 42.85], [-1.98, 43.32]],
    "A-2":  [[-3.70, 40.42], [-3.17, 40.63], [-2.10, 41.20], [-0.89, 41.65], [0.62, 41.61], [2.18, 41.39]],
    "A-3":  [[-3.70, 40.42], [-3.00, 40.01], [-2.14, 40.07], [-1.10, 39.49], [-0.38, 39.47]],
    "A-4":  [[-3.70, 40.42], [-3.60, 40.03], [-3.37, 38.99], [-3.78, 38.09], [-4.78, 37.89], [-5.99, 37.39]],
    "A-5":  [[-3.70, 40.42], [-4.83, 39.96], [-5.88, 39.46], [-6.34, 38.92], [-6.97, 38.88]],
    "A-6":  [[-3.70, 40.42], [-4.12, 40.95], [-4.72, 41.65], [-6.20, 42.30], [-7.56, 43.01], [-8.40, 43.37]],
    "AP-7": [[2.18, 41.39], [1.24, 41.12], [0.50, 40.50], [-0.38, 39.47], [-0.48, 38.35], [-1.13, 37.98]],
    "A-8":  [[-1.79, 43.34], [-1.98, 43.32], [-2.93, 43.26], [-3.81, 43.46], [-5.85, 43.36], [-7.56, 43.01], [-8.40, 43.37]],
    "A-66": [[-5.99, 37.39], [-6.34, 38.92], [-6.37, 39.47], [-6.00, 40.20], [-5.66, 40.97], [-5.75, 41.50], [-5.57, 42.60], [-5.85, 43.36]],
    "A-23": [[-0.27, 39.68], [-0.60, 39.80], [-1.11, 40.34], [-0.50, 41.35], [0.20, 42.79]],
    "A-45": [[-4.78, 37.89], [-4.56, 37.50], [-4.42, 36.72]],
    "A-92": [[-5.99, 37.39], [-5.20, 37.39], [-4.56, 37.02], [-3.60, 37.18], [-3.14, 37.30], [-2.46, 36.84]],
}

CORRIDOR_COLORS: dict[str, list[int]] = {
    "A-1": [99, 179, 237],
    "A-2": [154, 205, 100],
    "A-3": [246, 173, 85],
    "A-4": [237, 100, 100],
    "A-5": [183, 148, 246],
    "A-6": [252, 211, 77],
    "AP-7": [56, 189, 248],
    "A-8": [52, 211, 153],
    "A-66": [251, 146, 60],
    "A-23": [167, 139, 250],
    "A-45": [244, 114, 182],
    "A-92": [94, 234, 212],
}

GRID_COLORS = {
    "Sufficient": [34, 197, 94, 220],
    "Moderate":   [234, 179, 8, 220],
    "Congested":  [239, 68, 68, 220],
}
