# Applications with similar behavior throughout multiple executions

## cp2k

Total filtered entries: 198 out of 216, 91.67% have IO time less than 60 seconds.

![Clustering](docs/cp2k_filter.png)

**Characteristics**
- All entries are part of one cluster. 
- 33 features (out of 199) have different values on all rows.
- High variation within values of these features are due only to the two outliers (visible in the figure above)
- Average values and variation for all 33 features can be found in `docs/cp2k_features.txt`

## NWChem

Total filtered entries: 215 out of 231, 93.07% have IO time less than 60 seconds.

![Clustering](docs/nwchem_filter.png)

**Characteristics**
- All entries are part of one cluster. 
- 47 features (out of 199) have different values on all rows.
- High variation within values of these features are due only to outliers
- Average values and variation for all 47 features can be found in `docs/nwchem_features.txt`

![Clustering](docs/nwchem_apps.png)

NWChem might have a more diverse behavior (based on the submission characteristics, specifically the number of requested nodes). We need to add more input data to be sure. 
