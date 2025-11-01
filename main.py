# main.py

import math
import pandas as pd
import re

EARTH_RADIUS_KM = 6371.0088

def _extract_lon_lat(value):
    """
    Extract lon/lat from strings like:
      - POINT (-73.4764687 41.072882)
      - (-73.4764687, 41.072882)
      - -73.4764687 41.072882
    Returns (lat, lon) as floats or (None, None) on failure.
    """
    if pd.isna(value):
        return None, None
    s = str(value).strip()

    # Try POINT (lon lat)
    m = re.search(r"POINT\s*\(\s*([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\s*\)", s, re.IGNORECASE)
    if m:
        lon = float(m.group(1)); lat = float(m.group(2))
        return lat, lon

    # Try "(lon, lat)" style
    m = re.search(r"\(?\s*([-+]?\d+\.?\d*)\s*[,\s]\s*([-+]?\d+\.?\d*)\s*\)?", s)
    if m:
        a = float(m.group(1)); b = float(m.group(2))
        # Heuristic: if first value is between -180 and 180 and second between -90 and 90,
        # it could be lon, lat or lat, lon. We assume typical POINT form was lon lat; if unclear, try to guess.
        # If |a|>90 => a is longitude, b latitude.
        if abs(a) > 90 and abs(b) <= 90:
            lon, lat = a, b
        elif abs(b) > 90 and abs(a) <= 90:
            lon, lat = b, a
        else:
            # default: first = lon, second = lat (matches many datasets)
            lon, lat = a, b
        return lat, lon

    return None, None

def haversine_vectorized(lat1, lon1, lat2_arr, lon2_arr):
    """
    Vectorized haversine (returns distances in km)
    lat1, lon1 are scalars in degrees
    lat2_arr, lon2_arr are 1D arrays/Series in degrees
    """
    lat1_r = math.radians(lat1)
    lon1_r = math.radians(lon1)
    lat2_r = lat2_arr.apply(math.radians)
    lon2_r = lon2_arr.apply(math.radians)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (dlat/2).apply(math.sin)**2 + (lat2_r.apply(math.cos) * math.cos(lat1_r) * (dlon/2).apply(math.sin)**2)
    # safer calculation of c
    c = 2 * a.apply(lambda x: math.asin(min(1, math.sqrt(x))))
    return EARTH_RADIUS_KM * c

def load_and_prepare(csv_path="Electric_Vehicle_Charging_Stations.csv"):
    """
    Loads CSV and returns DataFrame with reliable 'latitude' and 'longitude' columns.
    Also normalizes charger counts to ints (columns with suffix _num).
    """
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    # Find geo column name (try exact, then fuzzy)
    geo_col = None
    for candidate in ["New Georeferenced Column", "New Georeferenced Column ", "Georeferenced", "geometry", "geom"]:
        if candidate in df.columns:
            geo_col = candidate
            break
    if geo_col is None:
        # fallback: find any column containing "point" in sample values
        for c in df.columns:
            sample = " ".join(df[c].astype(str).head(20).tolist()).lower()
            if "point" in sample or "(" in sample:
                geo_col = c
                break

    # Extract lat/lon robustly
    lat_list = []
    lon_list = []
    for v in df[geo_col] if geo_col in df.columns else [""]*len(df):
        lat, lon = _extract_lon_lat(v)
        lat_list.append(lat)
        lon_list.append(lon)

    df["latitude"] = pd.Series(lat_list)
    df["longitude"] = pd.Series(lon_list)

    # Filter rows without coords
    df = df[df["latitude"].notnull() & df["longitude"].notnull()].copy()
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)

    # Normalize charger count columns if exist, else create zeros
    def to_int_safe(x):
        x = str(x)
        m = re.search(r"(\d+)", x)
        return int(m.group(1)) if m else 0

    for original in ["EV Level1 EVSE Num", "EV Level2 EVSE Num", "EV DC Fast Count"]:
        target = original + "_num"
        if original in df.columns:
            df[target] = df[original].apply(to_int_safe)
        else:
            df[target] = 0

    # Return df
    return df.reset_index(drop=True)

def find_nearest(df, query_lat, query_lon, k=5):
    """
    Returns a list of dicts with nearest k stations to (query_lat, query_lon).
    """
    if df is None or len(df) == 0:
        return []

    # compute distances (vectorized)
    distances = haversine_vectorized(query_lat, query_lon, df["latitude"], df["longitude"])
    df = df.copy()
    df["distance_km"] = distances

    nearest_df = df.nsmallest(min(k, len(df)), "distance_km")

    results = []
    for _, row in nearest_df.iterrows():
        results.append({
            "station_name": row.get("Station Name", ""),
            "street_address": row.get("Street Address", ""),
            "city": row.get("City", ""),
            "access": row.get("Access Days Time", ""),
            "level1": int(row.get("EV Level1 EVSE Num_num", row.get("EV Level1 EVSE Num_num", 0))) if "EV Level1 EVSE Num_num" in row.index else int(row.get("EV Level1 EVSE Num_num", 0)),
            "level2": int(row.get("EV Level2 EVSE Num_num", row.get("EV Level2 EVSE Num_num", 0))) if "EV Level2 EVSE Num_num" in row.index else int(row.get("EV Level2 EVSE Num_num", 0)),
            "dc_fast": int(row.get("EV DC Fast Count_num", row.get("EV DC Fast Count_num", 0))) if "EV DC Fast Count_num" in row.index else int(row.get("EV DC Fast Count_num", 0)),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "distance_km": float(round(row["distance_km"], 4))
        })
    return results

if __name__ == "__main__":
    df = load_and_prepare()
    print("Loaded stations:", len(df))
    if len(df) > 0:
        # quick check using first station coords as query (should return self at distance 0)
        test = find_nearest(df, df.iloc[0]["latitude"], df.iloc[0]["longitude"], k=3)
        print("Test nearest:", test[:2])
