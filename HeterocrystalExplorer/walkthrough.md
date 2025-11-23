# QD-Perovskite Heterocrystal Explorer Walkthrough

This tool helps you identify compatible Quantum Dot (QD) and Perovskite pairs for colloidal heterocrystal synthesis. It uses the Materials Project API to fetch real material data and calculates lattice mismatch and band alignment metrics.

## Features
- **Search**: Find Perovskites and Quantum Dots by chemical formula (e.g., "CsPbBr3", "PbS").
- **Screening Database**: Automatically discover compatible pairs by filtering a database of common materials by lattice strain and bandgap.
- **Analysis**: Calculate lattice strain and visualize band gap differences.
- **Visualization**: Interactive band diagram and strain indicators.

## How to Run
1. **Prerequisites**: Ensure you have Python installed with the dependencies:
   ```bash
   pip install mp-api pymatgen fastapi uvicorn
   ```
2. **Start the Server**:
   Run the following command in the project root:
   ```bash
   python backend/main.py
   ```
3. **Access the App**:
   Open your browser and navigate to:
   [http://localhost:8000](http://localhost:8000)

## Usage Guide
### Single Pair Analysis
1. **Select Perovskite**: Enter a formula (e.g., `CsPbBr3`) and click Search. Select a candidate from the list.
2. **Select Quantum Dot**: Enter a formula (e.g., `PbS`) and click Search. Select a candidate.
3. **Analyze**: Click "Analyze Heterojunction" to see the results.

### Screening Database
1. Switch to the **Screening Database** tab.
2. Set your criteria:
   - **Max Lattice Mismatch**: e.g., 5.0%
   - **Perovskite Bandgap**: e.g., 1.5 - 3.0 eV (Visible)
   - **QD Bandgap**: e.g., 0.0 - 1.5 eV (NIR)
3. Click **Find Compatible Pairs**.
4. Browse the table of results, sorted by lowest lattice strain.

## Troubleshooting
- **API Key**: The tool uses a hardcoded API key. If you hit rate limits, you may need to provide your own in `backend/main.py`.
- **No Results**: Ensure the formula is correct and exists in the Materials Project database.
