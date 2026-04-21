"""
Generates all 4 static HTML maps from output CSVs — no notebook re-run needed.

    python notebooks/generate_maps.py

Outputs written to streamlit_app/static/maps/:
    map1.html           — Proposed HPC stations (File 2)
    map2.html           — Friction points / Congested grid (File 3)
    map3.html           — Strategic markets / province opportunity
    map4_pois.html      — Points of interest along corridors
    bi_map_optimized.html — Full BI overview (all layers)
"""

from pathlib import Path
import json
import pandas as pd
import folium

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent.parent
OUT_DIR    = ROOT / "notebooks" / "outputs"
DATA_DIR   = ROOT / "streamlit_app" / "data"
STATIC_DIR = ROOT / "streamlit_app" / "static" / "maps"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# ── Shared constants ───────────────────────────────────────────────────────────
STATUS_COLOR = {
    "Sufficient": "#27ae60",
    "Moderate":   "#f39c12",
    "Congested":  "#e74c3c",
}
QUADRANT_COLOR = {
    "Leader":   "#00A9CE",
    "Mature":   "#7DC855",
    "Emerging": "#F5A623",
    "Lagging":  "#64748B",
}
CORRIDOR_COLORS = {
    "A-1": "#63b3ed", "A-2": "#9acd64", "A-3": "#f6ad55",
    "A-4": "#ed6464", "A-5": "#b794f6", "A-6": "#fcd34d",
    "AP-7": "#38bdf8", "A-8": "#34d399", "A-66": "#fb923c",
    "A-23": "#a78bfa", "A-45": "#f472b6", "A-92": "#5eead4",
}
CORRIDORS = {
    "A-1":  [[40.42,-3.70],[41.67,-3.68],[42.35,-3.70],[42.68,-2.94],[42.85,-2.67],[43.32,-1.98]],
    "A-2":  [[40.42,-3.70],[40.63,-3.17],[41.20,-2.10],[41.65,-0.89],[41.61,0.62],[41.39,2.18]],
    "A-3":  [[40.42,-3.70],[40.01,-3.00],[40.07,-2.14],[39.49,-1.10],[39.47,-0.38]],
    "A-4":  [[40.42,-3.70],[40.03,-3.60],[38.99,-3.37],[38.09,-3.78],[37.89,-4.78],[37.39,-5.99]],
    "A-5":  [[40.42,-3.70],[39.96,-4.83],[39.46,-5.88],[38.92,-6.34],[38.88,-6.97]],
    "A-6":  [[40.42,-3.70],[40.95,-4.12],[41.65,-4.72],[42.30,-6.20],[43.01,-7.56],[43.37,-8.40]],
    "AP-7": [[41.39,2.18],[41.12,1.24],[40.50,0.50],[39.47,-0.38],[38.35,-0.48],[37.98,-1.13]],
    "A-8":  [[43.34,-1.79],[43.32,-1.98],[43.26,-2.93],[43.46,-3.81],[43.36,-5.85],[43.01,-7.56],[43.37,-8.40]],
    "A-66": [[37.39,-5.99],[38.92,-6.34],[39.47,-6.37],[40.20,-6.00],[40.97,-5.66],[41.50,-5.75],[42.60,-5.57],[43.36,-5.85]],
    "A-23": [[39.68,-0.27],[39.80,-0.60],[40.34,-1.11],[41.35,-0.50],[42.79,0.20]],
    "A-45": [[37.89,-4.78],[37.50,-4.56],[36.72,-4.42]],
    "A-92": [[37.39,-5.99],[37.39,-5.20],[37.02,-4.56],[37.18,-3.60],[37.30,-3.14],[36.84,-2.46]],
}

SPAIN = [40.2, -3.5]

IDE_NODES = {"IBE_020", "IBE_022", "IBE_024", "IBE_030", "IBE_031"}


def _add_corridors(m, show=True):
    fg = folium.FeatureGroup(name="🛣️ TEN-T Corridors", show=show)
    for name, pts in CORRIDORS.items():
        folium.PolyLine(
            locations=pts,
            color=CORRIDOR_COLORS.get(name, "#888"),
            weight=3, opacity=0.7,
            tooltip=name,
        ).add_to(fg)
    fg.add_to(m)


def _legend(html: str, m: folium.Map):
    m.get_root().html.add_child(folium.Element(html))


def _save(m: folium.Map, name: str):
    path = STATIC_DIR / name
    m.save(str(path))
    size = path.stat().st_size / 1e6
    print(f"  {name:<30} {size:.2f} MB")


# ══════════════════════════════════════════════════════════════════════════════
# MAP 1 — Proposed HPC Stations (File 2)
# ══════════════════════════════════════════════════════════════════════════════
def build_map1():
    file2 = pd.read_csv(OUT_DIR / "File 2.csv")
    m = folium.Map(location=SPAIN, zoom_start=6, tiles="CartoDB positron")
    _add_corridors(m)

    fg = folium.FeatureGroup(name="🔌 Proposed Stations (190)", show=True)
    for _, row in file2.iterrows():
        color = STATUS_COLOR.get(row["grid_status"], "#888")
        site  = str(row.get("site_name", "")).strip()
        site  = site if site and site not in ("nan", "NaN") else \
                row.get("category", "").replace("_", " ").title()
        popup = (
            f"<b>{row['location_id']}</b><br>"
            f"Corridor: {row['route_segment']}<br>"
            f"Site: {site}<br>"
            f"Chargers: {int(row['n_chargers_proposed'])} × 150 kW<br>"
            f"Demand: {int(row['estimated_demand_kw']):,} kW<br>"
            f"Grid: <b style='color:{color}'>{row['grid_status']}</b><br>"
            f"Distributor: {row.get('distributor_network', '—')}<br>"
            f"Score: {row['composite_score']:.3f}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=7 + int(row["n_chargers_proposed"]) // 3,
            color=color, weight=2,
            fill=True, fill_color=color, fill_opacity=0.85,
            popup=folium.Popup(popup, max_width=260),
            tooltip=f"{row['location_id']} | {row['grid_status']} | Score {row['composite_score']:.3f}",
        ).add_to(fg)
    fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    _legend("""
<div style="position:fixed;bottom:30px;left:30px;z-index:9999;
     background:rgba(15,23,42,0.92);padding:14px 18px;border-radius:10px;
     font-size:12px;color:#F1F5F9;border:1px solid #334155;">
  <b>🔌 Map 1 — Proposed Stations</b><br><br>
  <b>Grid Status</b><br>
  <span style="color:#27ae60;">●</span> Sufficient (&ge;5 MW) — build now<br>
  <span style="color:#f39c12;">●</span> Moderate (1–5 MW) — minor upgrade<br>
  <span style="color:#e74c3c;">●</span> Congested (&lt;1 MW) — reinforce grid<br><br>
  <i style="color:#94A3B8;">Circle size = chargers proposed</i>
</div>""", m)
    _save(m, "map1.html")


# ══════════════════════════════════════════════════════════════════════════════
# MAP 2 — Grid Friction Points (File 3)
# ══════════════════════════════════════════════════════════════════════════════
def build_map2():
    file2 = pd.read_csv(OUT_DIR / "File 2.csv")
    file3 = pd.read_csv(OUT_DIR / "File 3.csv")
    m = folium.Map(location=SPAIN, zoom_start=6, tiles="CartoDB positron")
    _add_corridors(m)

    # All proposed stations (faded background)
    fg_all = folium.FeatureGroup(name="🔌 All Proposed Stations", show=True)
    for _, row in file2.iterrows():
        color = STATUS_COLOR.get(row["grid_status"], "#888")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5, color=color, weight=1,
            fill=True, fill_color=color, fill_opacity=0.4,
            tooltip=f"{row['location_id']} | {row['grid_status']}",
        ).add_to(fg_all)
    fg_all.add_to(m)

    # Friction points highlighted
    fg_fric = folium.FeatureGroup(name="⚡ Friction Points (164)", show=True)
    top10_ids = set(
        file2[file2["grid_status"] == "Congested"]
        .nlargest(10, "composite_score")["location_id"]
    )
    for _, row in file3.iterrows():
        status = row.get("grid_status", "Congested")
        color  = STATUS_COLOR.get(status, "#e74c3c")
        is_top = row["bottleneck_id"].replace("FRIC_", "IBE_") in top10_ids or \
                 row.get("bottleneck_id", "") in top10_ids
        popup = (
            f"<b>{row['bottleneck_id']}</b><br>"
            f"Corridor: {row['route_segment']}<br>"
            f"Demand: {int(row['estimated_demand_kw']):,} kW<br>"
            f"Grid: <b style='color:{color}'>{status}</b><br>"
            f"Distributor: {row.get('distributor_network', '—')}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=9 if is_top else 7,
            color="#fff", weight=2,
            fill=True, fill_color=color, fill_opacity=0.9,
            popup=folium.Popup(popup, max_width=250),
            tooltip=f"{row['bottleneck_id']} | {row.get('distributor_network','—')}",
        ).add_to(fg_fric)
    fg_fric.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    _legend("""
<div style="position:fixed;bottom:30px;left:30px;z-index:9999;
     background:rgba(15,23,42,0.92);padding:14px 18px;border-radius:10px;
     font-size:12px;color:#F1F5F9;border:1px solid #334155;">
  <b>⚡ Map 2 — Grid Friction Points</b><br><br>
  <span style="color:#f39c12;">●</span> Moderate grid constraint<br>
  <span style="color:#e74c3c;">●</span> Congested — reinforce first<br><br>
  <i style="color:#94A3B8;">164 friction points total<br>
  Click any marker for details</i>
</div>""", m)
    _save(m, "map2.html")


# ══════════════════════════════════════════════════════════════════════════════
# MAP 3 — Strategic Markets / Province Opportunity
# ══════════════════════════════════════════════════════════════════════════════
def build_map3():
    em = pd.read_csv(DATA_DIR / "emerging_markets_ranking.csv")
    em["cagr_pct"] = (em["cagr"] * 100).round(1)

    geojson_path = DATA_DIR / "spain_provinces.geojson"
    with open(geojson_path, encoding="utf-8") as f:
        geojson = json.load(f)

    # Build lookup: province_code → row
    lookup = {
        str(row["province_code"]).zfill(2): row
        for _, row in em.iterrows()
    }

    m = folium.Map(location=SPAIN, zoom_start=6, tiles="CartoDB positron")

    def style_fn(feature):
        code = str(feature["properties"].get("cod_prov", "")).zfill(2)
        row  = lookup.get(code)
        if row is None:
            return {"fillColor": "#1E293B", "color": "#334155",
                    "weight": 1, "fillOpacity": 0.5}
        color = QUADRANT_COLOR.get(row["quadrant"], "#64748B")
        return {"fillColor": color, "color": "#0F172A",
                "weight": 1, "fillOpacity": 0.7}

    def tooltip_fn(feature):
        code = str(feature["properties"].get("cod_prov", "")).zfill(2)
        row  = lookup.get(code)
        if row is None:
            return folium.Tooltip("No data")
        return folium.Tooltip(
            f"<b>{row['province_name']}</b> · {row['auto_community']}<br>"
            f"Quadrant: <b>{row['quadrant']}</b><br>"
            f"CAGR: {row['cagr_pct']}% · Fleet 2027: {int(row['ev_fleet_2027']):,}<br>"
            f"Opportunity Score: {row['opportunity_score']:.1f}"
        )

    fg_prov = folium.FeatureGroup(name="📍 Province Opportunity", show=True)
    folium.GeoJson(
        geojson,
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=[], labels=False,
        ),
    ).add_to(fg_prov)
    fg_prov.add_to(m)

    # Add province labels for top 10 Emerging
    fg_labels = folium.FeatureGroup(name="🏷️ Top Emerging Labels", show=True)
    top_emerging = em[em["quadrant"] == "Emerging"].nlargest(10, "opportunity_score")
    for feat in geojson["features"]:
        code = str(feat["properties"].get("cod_prov", "")).zfill(2)
        row  = lookup.get(code)
        if row is None or row["province_name"] not in top_emerging["province_name"].values:
            continue
        # Compute rough centroid from bbox
        coords = feat["geometry"]["coordinates"]
        all_pts = []
        def collect(c):
            if isinstance(c[0], list):
                for sub in c:
                    collect(sub)
            else:
                all_pts.append(c)
        collect(coords)
        if not all_pts:
            continue
        lat = sum(p[1] for p in all_pts) / len(all_pts)
        lon = sum(p[0] for p in all_pts) / len(all_pts)
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(
                html=(
                    f"<div style='font-size:9px;font-weight:bold;color:#1E293B;"
                    f"background:#F5A623;padding:2px 5px;border-radius:4px;"
                    f"white-space:nowrap;'>{row['province_name']}<br>"
                    f"CAGR {row['cagr_pct']}%</div>"
                ),
                icon_size=(90, 30), icon_anchor=(45, 15),
            ),
            tooltip=(
                f"{row['province_name']} | CAGR {row['cagr_pct']}% | "
                f"Score {row['opportunity_score']:.1f}"
            ),
        ).add_to(fg_labels)
    fg_labels.add_to(m)

    _add_corridors(m, show=False)
    folium.LayerControl(collapsed=False).add_to(m)
    _legend("""
<div style="position:fixed;bottom:30px;left:30px;z-index:9999;
     background:rgba(15,23,42,0.92);padding:14px 18px;border-radius:10px;
     font-size:12px;color:#F1F5F9;border:1px solid #334155;">
  <b>📈 Map 3 — Strategic Markets</b><br><br>
  <span style="color:#F5A623;">■</span> Emerging — high CAGR, low fleet<br>
  <span style="color:#00A9CE;">■</span> Leader — high CAGR, high fleet<br>
  <span style="color:#7DC855;">■</span> Mature — moderate growth<br>
  <span style="color:#64748B;">■</span> Lagging — slow adoption<br><br>
  <i style="color:#94A3B8;">Labels = Top 10 Emerging provinces</i>
</div>""", m)
    _save(m, "map3.html")


# ══════════════════════════════════════════════════════════════════════════════
# MAP 4 — Points of Interest along corridors
# ══════════════════════════════════════════════════════════════════════════════
def build_map4():
    pois = pd.read_csv(OUT_DIR / "pois_all.csv")

    # Keep only corridor-relevant categories, cap at 3000 per category
    keep_cats = ["petrol_station", "hotel", "motorway_junction", "train_station"]
    pois = pois[pois["category"].isin(keep_cats)].copy()
    pois = (
        pois.groupby("category", group_keys=False)
        .apply(lambda g: g.sample(min(len(g), 800), random_state=42))
        .reset_index(drop=True)
    )

    CAT_COLOR = {
        "petrol_station":    "#f39c12",
        "hotel":             "#00A9CE",
        "motorway_junction": "#7DC855",
        "train_station":     "#a78bfa",
    }
    CAT_ICON = {
        "petrol_station":    "⛽",
        "hotel":             "🏨",
        "motorway_junction": "🚗",
        "train_station":     "🚂",
    }

    m = folium.Map(location=SPAIN, zoom_start=6, tiles="CartoDB positron")
    _add_corridors(m)

    for cat in keep_cats:
        df_cat = pois[pois["category"] == cat]
        color  = CAT_COLOR[cat]
        icon   = CAT_ICON[cat]
        fg = folium.FeatureGroup(name=f"{icon} {cat.replace('_',' ').title()} ({len(df_cat)})", show=(cat == "petrol_station"))
        for _, row in df_cat.iterrows():
            name = str(row.get("name", "")).strip()
            name = name if name and name not in ("nan", "NaN") else cat.replace("_", " ").title()
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=5,
                color=color, weight=1,
                fill=True, fill_color=color, fill_opacity=0.75,
                tooltip=f"{icon} {name}",
            ).add_to(fg)
        fg.add_to(m)

    # Overlay proposed stations
    file2 = pd.read_csv(OUT_DIR / "File 2.csv")
    fg_prop = folium.FeatureGroup(name="🔌 Proposed Stations", show=True)
    for _, row in file2.iterrows():
        color = STATUS_COLOR.get(row["grid_status"], "#888")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8, color="#fff", weight=2,
            fill=True, fill_color=color, fill_opacity=0.9,
            tooltip=f"{row['location_id']} | {row['grid_status']}",
        ).add_to(fg_prop)
    fg_prop.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    _legend("""
<div style="position:fixed;bottom:30px;left:30px;z-index:9999;
     background:rgba(15,23,42,0.92);padding:14px 18px;border-radius:10px;
     font-size:12px;color:#F1F5F9;border:1px solid #334155;">
  <b>📍 Map 4 — Points of Interest</b><br><br>
  <span style="color:#f39c12;">●</span> Petrol stations<br>
  <span style="color:#00A9CE;">●</span> Hotels<br>
  <span style="color:#7DC855;">●</span> Motorway junctions<br>
  <span style="color:#a78bfa;">●</span> Train stations<br>
  <span style="color:#27ae60;">●</span> Proposed HPC station<br>
</div>""", m)
    _save(m, "map4_pois.html")


# ══════════════════════════════════════════════════════════════════════════════
# BI MAP — Full overview (reuse generate_bi_map_optimized logic inline)
# ══════════════════════════════════════════════════════════════════════════════
def build_bi_map():
    file2 = pd.read_csv(OUT_DIR / "File 2.csv")
    file3 = pd.read_csv(OUT_DIR / "File 3.csv")
    m = folium.Map(location=SPAIN, zoom_start=6, tiles="CartoDB positron")
    _add_corridors(m)

    fg_proposed = folium.FeatureGroup(name="🔌 Proposed Stations (190)", show=True)
    for _, row in file2.iterrows():
        color = STATUS_COLOR.get(row["grid_status"], "#888")
        site  = str(row.get("site_name", "")).strip()
        site  = site if site and site not in ("nan", "NaN") else \
                row.get("category", "").replace("_", " ").title()
        popup = (
            f"<b>{row['location_id']}</b><br>"
            f"Corridor: {row['route_segment']}<br>"
            f"Site: {site}<br>"
            f"Chargers: {int(row['n_chargers_proposed'])} × 150 kW<br>"
            f"Demand: {int(row['estimated_demand_kw']):,} kW<br>"
            f"Grid: <b style='color:{color}'>{row['grid_status']}</b><br>"
            f"Distributor: {row.get('distributor_network', '—')}<br>"
            f"Score: {row['composite_score']:.3f}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=7, color=color, weight=2,
            fill=True, fill_color=color, fill_opacity=0.85,
            popup=folium.Popup(popup, max_width=250),
            tooltip=f"{row['location_id']} | {row['grid_status']}",
        ).add_to(fg_proposed)
    fg_proposed.add_to(m)

    fg_friction = folium.FeatureGroup(name="⚡ Friction Points (164)", show=True)
    for _, row in file3.iterrows():
        status = row.get("grid_status", "Congested")
        color  = STATUS_COLOR.get(status, "#e74c3c")
        popup = (
            f"<b>{row['bottleneck_id']}</b><br>"
            f"Corridor: {row['route_segment']}<br>"
            f"Demand: {int(row['estimated_demand_kw']):,} kW<br>"
            f"Grid: <b style='color:{color}'>{status}</b><br>"
            f"Distributor: {row.get('distributor_network', '—')}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6, color="#fff", weight=2,
            fill=True, fill_color=color, fill_opacity=0.9,
            popup=folium.Popup(popup, max_width=250),
            tooltip=f"{row['bottleneck_id']} | {status}",
        ).add_to(fg_friction)
    fg_friction.add_to(m)

    top10 = (
        file2[file2["grid_status"] == "Congested"]
        .nlargest(10, "composite_score")
        .reset_index(drop=True)
    )
    top10.index += 1
    fg_top10 = folium.FeatureGroup(name="🔴 Top 10 Priority (Congested)", show=True)
    for rank, row in top10.iterrows():
        is_ide = row["location_id"] in IDE_NODES
        color  = "#8B0000" if is_ide else "#e74c3c"
        border = "#FFD700" if is_ide else "#ffffff"
        site   = str(row.get("site_name", "")).strip()
        site   = site if site and site not in ("nan", "NaN") else \
                 row.get("category", "").replace("_", " ").title()
        popup = (
            f"<b>#{rank} — {row['location_id']}</b><br>"
            f"Corridor: <b>{row['route_segment']}</b><br>"
            f"Site: {site}<br>"
            f"Chargers: {int(row['n_chargers_proposed'])} × 150 kW<br>"
            f"Distributor: <b>{row.get('distributor_network', '—')}</b>"
            + ("<br><b style='color:#8B0000'>⭐ i-DE — self-authorise</b>" if is_ide
               else "<br>🔧 External — negotiation required")
            + f"<br>Score: {row['composite_score']:.3f}"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=14, color=border, weight=3,
            fill=True, fill_color=color, fill_opacity=0.95,
            popup=folium.Popup(popup, max_width=270),
            tooltip=f"#{rank} {row['location_id']} · {'i-DE ⭐' if is_ide else row.get('distributor_network','')}",
        ).add_to(fg_top10)
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.DivIcon(
                html=(
                    f"<div style='font-size:10px;font-weight:bold;color:white;"
                    f"background:{color};border:2px solid {border};border-radius:50%;"
                    f"width:22px;height:22px;display:flex;align-items:center;"
                    f"justify-content:center;'>{rank}</div>"
                ),
                icon_size=(22, 22), icon_anchor=(11, 11),
            ),
        ).add_to(fg_top10)
    fg_top10.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    _legend("""
<div style="position:fixed;bottom:30px;left:30px;z-index:9999;
     background:rgba(15,23,42,0.92);padding:14px 18px;border-radius:10px;
     font-size:12px;color:#F1F5F9;border:1px solid #334155;min-width:190px;">
  <b style="font-size:13px;">⚡ Iberdrola BI Map</b><br><br>
  <b>Grid Status</b><br>
  <span style="color:#27ae60;">●</span> Sufficient (&ge;5 MW)<br>
  <span style="color:#f39c12;">●</span> Moderate (1–5 MW)<br>
  <span style="color:#e74c3c;">●</span> Congested (&lt;1 MW)<br><br>
  <b>Top 10 Priority</b><br>
  <span style="color:#8B0000;">●</span> i-DE ⭐ fast-track<br>
  <span style="color:#e74c3c;">●</span> External distributor<br>
</div>""", m)
    _save(m, "bi_map_optimized.html")


# ── Run all ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating maps...\n")
    build_map1()
    build_map2()
    build_map3()
    build_map4()
    build_bi_map()
    print("\nAll maps written to streamlit_app/static/maps/")
