from mp_api.client import MPRester
from pymatgen.core import Structure
from typing import List, Dict, Optional

class MaterialsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_materials(self, formula: str) -> List[Dict]:
        """
        Search for materials by formula.
        Returns a list of dictionaries containing material_id, structure, and band_gap.
        """
        with MPRester(self.api_key) as mpr:
            # Using mpr.materials.summary as suggested by deprecation warning
            docs = mpr.materials.summary.search(
                formula=formula, 
                fields=["material_id", "structure", "band_gap", "formula_pretty", "is_stable"]
            )
            
            results = []
            for doc in docs:
                results.append({
                    "material_id": str(doc.material_id),
                    "formula": doc.formula_pretty,
                    "band_gap": doc.band_gap,
                    "structure": doc.structure, # This is a pymatgen Structure object
                    "is_stable": doc.is_stable,
                    "lattice_params": {
                        "a": doc.structure.lattice.a,
                        "b": doc.structure.lattice.b,
                        "c": doc.structure.lattice.c,
                        "alpha": doc.structure.lattice.alpha,
                        "beta": doc.structure.lattice.beta,
                        "gamma": doc.structure.lattice.gamma,
                    }
                })
            return results

    def get_material_details(self, material_id: str):
        """
        Get detailed information for a specific material ID.
        """
        with MPRester(self.api_key) as mpr:
            doc = mpr.materials.summary.get_data_by_id(
                material_id, 
                fields=["material_id", "structure", "band_gap", "formula_pretty", "is_stable"]
            )
            return doc

    def fetch_perovskite_candidates(self) -> List[Dict]:
        """
        Fetch common halide perovskites (ABX3).
        We search for *Pb*3 and *Sn*3 with Halides to approximate ABX3.
        """
        candidates = []
        formulas = ["*PbCl3", "*PbBr3", "*PbI3", "*SnCl3", "*SnBr3", "*SnI3"]
        
        with MPRester(self.api_key) as mpr:
            for f in formulas:
                try:
                    docs = mpr.materials.summary.search(
                        formula=f,
                        fields=["material_id", "structure", "band_gap", "formula_pretty", "is_stable"]
                    )
                    for doc in docs:
                        # Filter for 3 species to ensure likely ABX3 (A, B, X)
                        if len(doc.structure.composition.elements) == 3:
                            candidates.append({
                                "material_id": str(doc.material_id),
                                "formula": doc.formula_pretty,
                                "band_gap": doc.band_gap,
                                "structure": doc.structure,
                                "is_stable": doc.is_stable,
                                "lattice_params": {
                                    "a": doc.structure.lattice.a,
                                    "b": doc.structure.lattice.b,
                                    "c": doc.structure.lattice.c,
                                }
                            })
                except Exception as e:
                    print(f"Error fetching {f}: {e}")
                    continue
        
        # Deduplicate by material_id
        unique_candidates = {c['material_id']: c for c in candidates}.values()
        return list(unique_candidates)

    def fetch_qd_candidates(self) -> List[Dict]:
        """
        Fetch common quantum dot materials (Chalcogenides, Pnictides).
        """
        candidates = []
        # Common binary/ternary QD families
        formulas = ["CdS", "CdSe", "CdTe", "PbS", "PbSe", "PbTe", "ZnS", "ZnSe", "ZnTe", "InP", "InAs"]
        
        with MPRester(self.api_key) as mpr:
            for f in formulas:
                try:
                    docs = mpr.materials.summary.search(
                        formula=f,
                        fields=["material_id", "structure", "band_gap", "formula_pretty", "is_stable"]
                    )
                    for doc in docs:
                        candidates.append({
                            "material_id": str(doc.material_id),
                            "formula": doc.formula_pretty,
                            "band_gap": doc.band_gap,
                            "structure": doc.structure,
                            "is_stable": doc.is_stable,
                            "lattice_params": {
                                "a": doc.structure.lattice.a,
                                "b": doc.structure.lattice.b,
                                "c": doc.structure.lattice.c,
                            }
                        })
                except Exception as e:
                    print(f"Error fetching {f}: {e}")
                    continue
                    
        unique_candidates = {c['material_id']: c for c in candidates}.values()
        return list(unique_candidates)
