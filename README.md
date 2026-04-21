# SpanishElectricGrid

## Project Description

### The Challenge: Designing Tomorrow's Charging Network

Road transport plays a vital role in connecting people, goods, and economies across the globe. However, it also represents a significant source of carbon emissions. The transition toward electric mobility is key for a sustainable future. As the European Union and the world push for ambitious climate objectives, the rapid growth of electric vehicles (EVs) on our roads demands a robust, smart, and strategically distributed charging infrastructure.

Unlike traditional refueling networks, EV charging must be intricately linked with the electrical grid. One of the greatest hurdles to this transition is not just deciding where a charging point is geographically convenient, but understanding where the electrical grid can actually support it without facing severe congestion.

This project uses real-world public datasets to explore how we can realistically build the charging network of tomorrow — designing data-driven solutions that help plan the necessary infrastructure, optimizing the location of public-use charging points on interurban transport routes with the fewest stations possible, while simultaneously analyzing grid capacity limitations.

### Scope of Analysis

The analysis focuses on the **interurban transport network in Spain**. Proposed charging stations must be located on interurban roads (autopistas, autovías, or carreteras nacionales) as classified in the Ministry of Transport dataset. Stations within urban road sections are excluded regardless of municipality size.

While urban centers currently concentrate the highest volume of electric vehicles, the true bottleneck for massive EV adoption lies in long-distance travel and the phenomenon known as "range anxiety." For this reason, the project specifically excludes large urban centers from the primary focus, concentrating instead on modeling and optimizing connectivity between cities, regions, and major transport corridors.

Furthermore, the model cannot solely rely on traffic volumes, route distances, or geometrical placement. It must inherently incorporate the capacity and potential congestion of the electrical distribution grid. The electrical grid is not a homogenous blanket of infinite energy; its capacity varies drastically across the territory. A geographically perfect location for a charging station based on highway traffic might be entirely unfeasible if the local electrical substation lacks the capacity to support high-power chargers.

**Target Horizon: 2027 Strategy** — The analysis and the proposed charging network are designed for a 2027 operational scenario, using predictive models to project EV adoption and charging demand for that year.

---

## Notebook Structure — `notebooks/ChargingNetwork_Merged_v2_Robyn.ipynb`

The analysis is contained in a single end-to-end notebook divided into four major sections.

### 0. Setup & Imports

Environment configuration, library imports, and helper utilities used throughout the notebook.

---

### 1. Demand

Forecasts EV adoption across Spain to 2027, split into national and regional views.

#### 1.1 EV Fleet Forecast

- Exploratory analysis of historical EV registrations by vehicle type (BEV, PHEV, REEV+FCEV)
- Stationarity testing (Augmented Dickey-Fuller) and autocorrelation analysis (ACF / PACF)
- Four time-series models benchmarked: **ARIMA**, **SARIMA**, **Holt-Winters ETS**, **Prophet**
- Best model selected by RMSE/MAE — forecast to December 2027
- Output: `total_ev_projected_2027` — cumulative national EV fleet projection

#### 1.2 Demand per Region

- Province-level EV registrations (2021–2023) mapped to 52 Spanish provinces
- 2027 national forecast disaggregated by province share and year-on-year growth
- Autonomous Community aggregation and EV type mix per province
- Interactive choropleth map of projected 2027 EV demand
- Output: `province_demand_2027.csv`

---

### 2. Supply

Documents the existing charging and grid infrastructure along interurban corridors.

#### 2.1 Roads & Traffic

- Road network loaded from OpenStreetMap (interurban only: autopistas, autovías, carreteras nacionales)
- Traffic intensity data from the Ministry of Transport (MITMA)
- **Map 1** — Road Network & Traffic Intensity

#### 2.2 Existing Chargers

- DGT charger registry parsed and geocoded
- Existing public HPC chargers plotted along TEN-T corridors
- **Map 2** — Existing EV Charging Stations

#### 2.3 Power Grid

- Multi-distributor grid capacity loaded from CNMC data (Iberdrola i-DE, Endesa, Viesgo, etc.)
- Grid nodes classified by available hosting capacity (MW)
- **Map 3** — Grid Connection Capacity

#### 2.4 Points of Interest

- OpenStreetMap POI data: service areas, petrol stations, hotels, motorway junctions, train stations
- Candidate hosting sites identified along interurban corridors
- **Map 4** — Points of Interest

---

### 3. Combined Analysis — Charging Network Proposal

Scores, filters, and finalises the proposed charging station network.

#### 3.0 Pre-flight Checks

Schema validation: required columns, grid status values, and cross-file consistency rules.

#### 3.1 Baseline Audit

Count of existing interurban HPC chargers to establish the gap to AFIR 2027 targets.

#### 3.2 Candidate Site Scoring

Composite scoring pipeline weighting traffic volume, EV demand, grid capacity, AFIR spacing (40 km), and proximity to POIs. Each candidate receives a `composite_score`.

#### 3.3 Grid Status Assignment

Each candidate classified as **Sufficient** (≥5 MW), **Moderate** (1–5 MW), or **Congested** (<1 MW) based on nearest grid node capacity.

#### 3.4 Spatial Selection

AFIR-compliant spacing filter applied — stations selected to maximise network coverage with minimum count.

#### 3.5 File 2 — Proposed Charging Locations

190 proposed interurban HPC stations with charger counts, estimated demand (kW), grid status, distributor network, and composite score.

#### 3.6 Friction Points — File 3

164 friction points where projected EV demand exceeds grid hosting capacity. Classified as Moderate or Congested — these are the priority grid reinforcement targets.

#### 3.7 File 1 — Global Network KPIs (Scorecard)

National-level summary metrics: total proposed chargers, corridor coverage, grid status breakdown, AFIR compliance rate.

#### 3.8 Top 10 Priority Stations — Congested Grid

The 10 highest-scoring **Congested** stations — where grid reinforcement is the only barrier to deployment:

- **i-DE managed nodes** (IBE_020, 022, 024, 030, 031) — Iberdrola can self-authorise the substation upgrade (fast-track)
- **External distributor nodes** (Endesa / Viesgo) — require third-party negotiation
- Interactive BI map combining all layers: proposed stations, friction points, top 10 priority nodes, TEN-T corridors

#### 3.9 Output Compliance Check

Automated validation that all three output files conform to the required datathon schema.

---

### 4. Conclusion

Strategic proposal summary including:

- **Our Proposal** — phased deployment plan (Sufficient → i-DE Congested → External Congested)
- Top 10 priority stations with station-by-station breakdown
- Key findings across demand, supply, and grid capacity
- Recommended next steps with timeline (Q3 2026 → Q4 2026 → 2027)
- Why Iberdrola is best positioned to lead the network build-out

---

## Installation

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- pip (included with Python)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/vik01/SpanishElecticGrid.git
   cd SpanishElecticGrid
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - **Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **macOS / Linux:**

     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
