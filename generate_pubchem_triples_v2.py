"""
Generate PubChem triples using compound NAMES (not SMILES) as subjects
This makes them compatible with KG_3cols.spo format for entity matching
"""

import pandas as pd
from pubchem_mapper import PubChemMapper
import sys

def generate_pubchem_spo(input_csv, output_spo, smiles_column='smile'):
    """
    Generate SPO file with PubChem triples using compound NAMES as subjects
    Writes incrementally (line by line)
    """

    print(f"Loading data from {input_csv}")
    df = pd.read_csv(input_csv)
    unique_smiles = df[smiles_column].dropna().unique()

    print(f"Processing {len(unique_smiles)} unique compounds...")
    print(f"Output will be written to {output_spo}")
    print()

    mapper = PubChemMapper()

    # Open output file ONCE for writing
    with open(output_spo, 'w', encoding='utf-8') as f:
        total_triples = 0
        successful_mappings = 0

        for i, smiles in enumerate(unique_smiles):
            if i % 50 == 0:
                print(f"Processing {i}/{len(unique_smiles)} compounds... ({total_triples} triples so far)")

            mapping = mapper.smiles_to_pubchem(smiles)

            if not mapping:
                continue

            successful_mappings += 1
            compound_name = mapping['name'] or mapping['iupac_name'] or f"compound_{mapping['cid']}"

            # Generate triples using COMPOUND NAME as subject (not SMILES)
            triples = []

            # Triple 1: Type (IUPAC name or common name)
            if mapping['iupac_name']:
                triples.append(f"{compound_name}\trdf:type\t{mapping['iupac_name']}")

            if mapping['name'] and mapping['name'] != compound_name:
                triples.append(f"{compound_name}\tpubchem:commonName\t{mapping['name']}")

            # Triple 2: Molecular Formula
            if mapping['formula']:
                triples.append(f"{compound_name}\tpubchem:molecularFormula\t{mapping['formula']}")

            # Triple 3: Molecular Weight
            if mapping['weight']:
                triples.append(f"{compound_name}\tpubchem:molecularWeight\t{mapping['weight']}")

            # Triple 4: Link SMILES (so we can trace back to original compound)
            triples.append(f"{compound_name}\tpubchem:smiles\t{smiles}")

            # Triple 5: PubChem CID
            if mapping['cid']:
                triples.append(f"{compound_name}\tpubchem:cid\tPubChem:CID{mapping['cid']}")

            # Write triples IMMEDIATELY (incremental)
            for triple in triples:
                f.write(triple + '\n')
                total_triples += 1

        print()
        print(f"✓ Done!")
        print(f"  Successful mappings: {successful_mappings}/{len(unique_smiles)}")
        print(f"  Total triples generated: {total_triples}")
        print(f"  Written to: {output_spo}")

    # Save cache for future runs
    mapper._save_cache()

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 2:
        input_csv = sys.argv[1]
        output_spo = sys.argv[2]
    else:
        input_csv = './data/flat-data.csv'
        output_spo = './output/pubchem_triples.spo'

    generate_pubchem_spo(input_csv, output_spo)
