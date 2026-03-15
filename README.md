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
