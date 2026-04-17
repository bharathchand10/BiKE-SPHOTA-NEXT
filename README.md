 # BiKE-SPHOTA with PubChem Compound Enhancement                                                                                                                                       
                                                                                                                                                                                        
  Extension of [BiKE-SPHOTA](https://github.com/bharathchand10/BiKE-SPHOTA) with chemical ontology enrichment using PubChem data.                                                       
                                                                                                                                                                                        
  ## What's New   

  This enhancement adds PubChem chemical property triples to the knowledge graph, improving compound embeddings in K-BERT training.                                                     
   
  ## Additional Steps (Before Step 5 in BiKE-SPHOTA's readme file)                                                                                                                                                   
                  
  ### 4.5: Generate PubChem Triples

  ```bash
  cd BiKE_upgrade
  python3 generate_pubchem_triples_v2.py /path/to/flat-data.csv ./output/pubchem_triples.spo
                                                                                                                                                                                        
  Outputs: pubchem_triples.spo (compound names as subjects)
                                                                                                                                                                                        
  Copy to K-BERT folder:                                                                                                                                                                
  cp ./output/pubchem_triples.spo /path/to/K-BERT/brain/kgs/
                                                                                                                                                                                        
  5 (Modified): K-BERT Training

  Modified files:
  - brain/knowgraph.py - Added _merge_pubchem_triples() method
  - run_kbert_cls.py - Updated to load both KG files automatically                                                                                                                      
   
  Run training as usual:                                                                                                                                                                
  conda activate k_bert
  bash run.sh          
             
  Files Needed
                                                                                                                                                                                        
  BiKE_upgrade/
  ├── pubchem_mapper.py                                                                                                                                                                 
  ├── generate_pubchem_triples_v2.py
  └── simple_chebi_mapper.py
