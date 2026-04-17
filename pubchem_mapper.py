"""
PubChem-based SMILES to Triple Generator
Maps SMILES -> PubChem CID -> Extract chemical properties as triples
"""

import requests
import pandas as pd
import pickle
from pathlib import Path
import time

class PubChemMapper:
    """Maps SMILES to PubChem data and generates triples"""

    def __init__(self, cache_file="./cache/pubchem_cache.pkl"):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()
        self.pubchem_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def smiles_to_pubchem(self, smiles):
        """
        Map SMILES -> PubChem data
        Returns: {'cid': 3675, 'name': 'Phenelzine', 'iupac_name': '2-phenylethylhydrazine'}
        """
        if smiles in self.cache:
            return self.cache[smiles]

        try:
            # Step 1: SMILES -> PubChem CID
            resp = requests.get(
                f"{self.pubchem_url}/compound/smiles/{smiles}/cids/JSON",
                timeout=10
            )
            cids = resp.json().get('IdentifierList', {}).get('CID', [])
            if not cids:
                self.cache[smiles] = None
                return None

            cid = cids[0]
            time.sleep(0.2)

            # Step 2: Get compound properties
            resp = requests.get(
                f"{self.pubchem_url}/compound/cid/{cid}/property/IUPACName,MolecularFormula,MolecularWeight,Title/JSON",
                timeout=10
            )
            props = resp.json().get('PropertyTable', {}).get('Properties', [{}])[0]
            time.sleep(0.2)

            result = {
                'cid': cid,
                'name': props.get('Title', ''),
                'iupac_name': props.get('IUPACName', ''),
                'formula': props.get('MolecularFormula', ''),
                'weight': props.get('MolecularWeight', ''),
            }

            self.cache[smiles] = result
            return result

        except Exception as e:
            print(f"Error mapping {smiles}: {e}")
            self.cache[smiles] = None
            return None

    def batch_map(self, smiles_list):
        """Map multiple SMILES at once"""
        results = {}
        for i, smiles in enumerate(smiles_list):
            if i % 50 == 0:
                print(f"Mapping {i}/{len(smiles_list)}")
            results[smiles] = self.smiles_to_pubchem(smiles)

        self._save_cache()
        return results
