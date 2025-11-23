from mp_api.client import MPRester
import sys

API_KEY = "OW3UAobyENgvmSLfdLbnOulYoR6SHV2y"

def test_api():
    try:
        with MPRester(API_KEY) as mpr:
            print("Successfully connected to Materials Project API.")
            
            # Search for a common perovskite to check data availability
            print("Searching for CsPbBr3...")
            docs = mpr.summary.search(formula="CsPbBr3", fields=["material_id", "structure", "band_gap", "is_stable"])
            
            if docs:
                print(f"Found {len(docs)} entries for CsPbBr3.")
                doc = docs[0]
                print(f"Sample Material ID: {doc.material_id}")
                print(f"Band Gap: {doc.band_gap} eV")
                print(f"Lattice Parameters: {doc.structure.lattice.abc}")
            else:
                print("No docs found for CsPbBr3.")

            # Search for a common QD material
            print("\nSearching for PbS...")
            docs_qs = mpr.summary.search(formula="PbS", fields=["material_id", "structure", "band_gap"])
            if docs_qs:
                print(f"Found {len(docs_qs)} entries for PbS.")
                doc = docs_qs[0]
                print(f"Sample Material ID: {doc.material_id}")
                print(f"Lattice Parameters: {doc.structure.lattice.abc}")
            
    except Exception as e:
        print(f"Error connecting to API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
