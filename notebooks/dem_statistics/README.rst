The scripts and notebooks in this directory are used for the creation of the the plots and tables that can be found on these pages:

- https://rgitools.readthedocs.io/en/latest/dems.html#global-data-availability
- https://rgitools.readthedocs.io/en/latest/dems_subregions.html

In the following the steps necessary to create a new version of these statistics are described:

1. create a new RGI topo dataset with the **oggm/cli/prepro_levels.py** script within the oggm repository

2. adapt all variables within the **statistics_paths.py** script to valid local paths. The *prepro_path* variable has to point towards the RGI topo dataset

3. run the **post_all_dems.py** script to create statistics about the coverage of each DEM product that RGI is currently supporting. These statistics are saved as *.h5*-files.

4. run the **dem_post_quality_per_region.py** script to create the barplots and csv files visualizing the previously created *.h5*-files.

5. if you plan to **update the docs pages**: run the **create_dems_subregions_rst.ipynb** to move the new barplots and csv files to the correct directory within the repository and regenerate the **dems_subregions.rst**. The barplots and csv files also contain files for all RGI regions combined. These are used in the **dems.rst** file, **and have to be updated manually**.