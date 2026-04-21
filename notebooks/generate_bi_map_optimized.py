"""
Generates bi_map_optimized.html — a lightweight Streamlit-deployable BI map.

Uses only the three output CSVs + hardcoded corridor lines.
Target size: < 10 MB (vs 165 MB full notebook output).

Run from any terminal:
    python notebooks/generate_bi_map_optimized.py
"""

from pathlib import Path
import pandas as pd
import folium
from folium.plugins import MarkerCluster

OUT_DIR  = Path(__file__).parent / "outputs"
SAVE_PATH = OUT_DIR / "bi_map_optimized.html"

# ── Load output files ──────────────────────────────────────────────────────────
file2 = pd.read_csv(OUT_DIR / "File 2.csv")
file3 = pd.read_csv(OUT_DIR / "File 3.csv")

# ── Colour helpers ─────────────────────────────────────────────────────────────
STATUS_COLOR = {
    "Sufficient": "#27ae60",
    "Moderate":   "#f39c12",
    "Congested":  "#e74c3c",
}
CORRIDOR_COLORS = {
    "A-1":  "#63b3ed", "A-2":  "#9acd64", "A-3":  "#f6ad55",
    "A-4":  "#ed6464", "A-5":  "#b794f6", "A-6":  "#fcd34d",
    "AP-7": "#38bdf8", "A-8":  "#34d399", "A-66": "#fb923c",
    "A-23": "#a78bfa", "A-45": "#f472b6", "A-92": "#5eead4",
}

# ── TEN-T corridors (hardcoded waypoints [lat, lon]) ──────────────────────────
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

# ── Build map ──────────────────────────────────────────────────────────────────
m = folium.Map(
    location=[40.2, -3.5],
    zoom_start=6,
    tiles="CartoDB positron",
)

# Layer 1 — TEN-T corridor lines
fg_corridors = folium.FeatureGroup(name="🛣️ TEN-T Corridors", show=True)
for name, waypoints in CORRIDORS.items():
    color = CORRIDOR_COLORS.get(name, "#888")
    folium.PolyLine(
        locations=waypoints,
        color=color,
        weight=3,
        opacity=0.7,
        tooltip=name,
    ).add_to(fg_corridors)
fg_corridors.add_to(m)

# Layer 2 — Proposed stations (File 2), coloured by grid status
fg_proposed = folium.FeatureGroup(name="🔌 Proposed Stations (190)", show=True)
for _, row in file2.iterrows():
    color = STATUS_COLOR.get(row.get("grid_status", ""), "#888")
    site  = str(row.get("site_name", "")).strip()
    site  = site if site and site not in ("nan", "NaN") else row.get("category","").replace("_"," ").title()
    popup_html = (
        f"<b>{row['location_id']}</b><br>"
        f"Corridor: {row['route_segment']}<br>"
        f"Chargers: {int(row['n_chargers_proposed'])} × 150 kW<br>"
        f"Demand: {int(row['estimated_demand_kw']):,} kW<br>"
        f"Grid: <b style='color:{color}'>{row['grid_status']}</b><br>"
        f"Distributor: {row.get('distributor_network','—')}<br>"
        f"Score: {row['composite_score']:.3f}"
    )
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=7,
        color=color, weight=2,
        fill=True, fill_color=color, fill_opacity=0.85,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{row['location_id']} | {row['grid_status']}",
    ).add_to(fg_proposed)
fg_proposed.add_to(m)

# Layer 3 — Friction points (File 3), Moderate + Congested
fg_friction = folium.FeatureGroup(name="⚡ Friction Points (164)", show=True)
for _, row in file3.iterrows():
    status = row.get("grid_status", "Congested")
    color  = STATUS_COLOR.get(status, "#e74c3c")
    popup_html = (
        f"<b>{row['bottleneck_id']}</b><br>"
        f"Corridor: {row['route_segment']}<br>"
        f"Demand: {int(row['estimated_demand_kw']):,} kW<br>"
        f"Grid: <b style='color:{color}'>{status}</b><br>"
        f"Distributor: {row.get('distributor_network','—')}"
    )
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color="#fff", weight=2,
        fill=True, fill_color=color, fill_opacity=0.9,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{row['bottleneck_id']} | {status}",
    ).add_to(fg_friction)
fg_friction.add_to(m)

# Layer 4 — Top 10 Congested priority stations (highlighted)
IDE_NODES = {"IBE_020", "IBE_022", "IBE_024", "IBE_030", "IBE_031"}
top10_congested = (
    file2[file2["grid_status"] == "Congested"]
    .nlargest(10, "composite_score")
    .reset_index(drop=True)
)
top10_congested.index += 1

fg_top10 = folium.FeatureGroup(name="🔴 Top 10 Priority (Congested)", show=True)
for rank, row in top10_congested.iterrows():
    is_ide = row["location_id"] in IDE_NODES
    color  = "#8B0000" if is_ide else "#e74c3c"
    border = "#FFD700" if is_ide else "#ffffff"
    site   = str(row.get("site_name","")).strip()
    site   = site if site and site not in ("nan","NaN") else row.get("category","").replace("_"," ").title()
    popup_html = (
        f"<b>#{rank} — {row['location_id']}</b><br>"
        f"Corridor: <b>{row['route_segment']}</b><br>"
        f"Site: {site}<br>"
        f"Chargers: {int(row['n_chargers_proposed'])} × 150 kW<br>"
        f"Distributor: <b>{row.get('distributor_network','—')}</b>"
        + ("<br><b style='color:#8B0000'>⭐ i-DE — self-authorise upgrade</b>" if is_ide
           else "<br>🔧 External — negotiation required")
        + f"<br>Score: {row['composite_score']:.3f}"
    )
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=14,
        color=border, weight=3,
        fill=True, fill_color=color, fill_opacity=0.95,
        popup=folium.Popup(popup_html, max_width=270),
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

# ── Legend ─────────────────────────────────────────────────────────────────────
legend_html = """
<div style="position:fixed;bottom:30px;left:30px;z-index:9999;
     background:rgba(15,23,42,0.92);padding:14px 18px;border-radius:10px;
     font-size:12px;color:#F1F5F9;border:1px solid #334155;min-width:190px;">
  <b style="font-size:13px;">⚡ Iberdrola BI Map</b><br><br>
  <b>Grid Status</b><br>
  <span style="color:#27ae60;">●</span> Sufficient (&ge;5 MW)<br>
  <span style="color:#f39c12;">●</span> Moderate (1–5 MW)<br>
  <span style="color:#e74c3c;">●</span> Congested (&lt;1 MW)<br><br>
  <b>Top 10 Priority</b><br>
  <span style="color:#8B0000;">●</span> i-DE managed ⭐ (fast-track)<br>
  <span style="color:#e74c3c;">●</span> External distributor<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ── Layer control ──────────────────────────────────────────────────────────────
folium.LayerControl(collapsed=False).add_to(m)

# ── Save ───────────────────────────────────────────────────────────────────────
m.save(str(SAVE_PATH))
size_mb = SAVE_PATH.stat().st_size / 1e6
print(f"Saved: {SAVE_PATH}")
print(f"Size:  {size_mb:.1f} MB")
