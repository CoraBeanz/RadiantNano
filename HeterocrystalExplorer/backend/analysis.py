import numpy as np
from pymatgen.core import Structure

def calculate_lattice_mismatch(struct1: Structure, struct2: Structure) -> float:
    """
    Calculate the lattice mismatch between two structures.
    This is a simplified approximation using the cubic root of the volume per atom 
    or just comparing average lattice parameters for now.
    
    For a more robust heterojunction analysis, we should compare specific facets, 
    but for a high-throughput screening, we can compare the pseudocubic lattice constants.
    """
    # Calculate average lattice parameter (pseudocubic approximation)
    a1 = (struct1.lattice.a * struct1.lattice.b * struct1.lattice.c) ** (1/3)
    a2 = (struct2.lattice.a * struct2.lattice.b * struct2.lattice.c) ** (1/3)
    
    mismatch = abs(a1 - a2) / min(a1, a2) * 100
    return mismatch

def analyze_band_alignment(bg1: float, bg2: float) -> str:
    """
    Analyze the potential band alignment based on band gaps.
    Note: Without absolute vacuum levels (electron affinity), we can't definitively 
    determine Type I, II, or III. 
    
    However, we can categorize based on the difference in band gaps which drives 
    confinement potential if offsets are favorable.
    
    For this demo, we will return a descriptive string about the band gap difference.
    """
    # This is a placeholder for more complex logic if we had electron affinity data.
    # MP data for electron affinity is sparse/calculated.
    
    diff = abs(bg1 - bg2)
    return f"Band gap difference: {diff:.2f} eV"

def get_heterojunction_metrics(mat1: dict, mat2: dict) -> dict:
    """
    Calculate metrics for a pair of materials.
    """
    strain = calculate_lattice_mismatch(mat1['structure'], mat2['structure'])
    alignment = analyze_band_alignment(mat1['band_gap'], mat2['band_gap'])
    
    return {
        "material1": mat1['formula'],
        "material2": mat2['formula'],
        "lattice_mismatch_percent": round(strain, 2),
        "band_gap_1": mat1['band_gap'],
        "band_gap_2": mat2['band_gap'],
        "band_alignment_note": alignment
    }
