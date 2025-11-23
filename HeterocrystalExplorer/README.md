# Heterocrystal Explorer

A powerful tool for discovering and analyzing perovskite-quantum dot heterojunctions for optoelectronic applications.

## Features

-   **Material Discovery**: Search the Materials Project database for Perovskites (e.g., CsPbBr3) and Quantum Dots (e.g., PbS).
-   **Heterojunction Analysis**:
    -   **Lattice Mismatch**: Calculates the lattice strain between two materials to predict epitaxial compatibility.
    -   **Band Alignment**: Visualizes the band gaps and offsets (Type I, II, etc.) to assess charge transfer potential.
-   **Screening Database**:
    -   Bulk screen thousands of material combinations.
    -   Filter by maximum lattice strain, bandgap ranges, and emission colors.
    -   Sort results by strain, bandgap, or material name.
-   **Detailed Visualization**:
    -   Interactive 3D crystal structure viewer for both materials.
    -   Detailed property breakdown (Stability, Crystal System, Spacegroup).

## Installation

1.  Clone the repository.
2.  Navigate to the `HeterocrystalExplorer` directory.
3.  Install dependencies:
    ```bash
    pip install fastapi uvicorn mp-api pymatgen python-dotenv
    ```
4.  Set up your Materials Project API key:
    -   Create a `.env` file in the project root.
    -   Add `MP_API_KEY=your_api_key_here`.

## Usage

1.  Start the server:
    ```bash
    python backend/main.py
    ```
2.  Open your browser to `http://localhost:8000`.

## Technologies

-   **Backend**: Python, FastAPI, Pymatgen, Materials Project API
-   **Frontend**: HTML5, CSS3, JavaScript, Chart.js, 3Dmol.js
