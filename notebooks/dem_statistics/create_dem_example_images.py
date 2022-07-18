import papermill as pm
import os
import os.path as path
# these names and RGIids are taken from the "Examples" on this page: https://rgitools.readthedocs.io/en/latest/dems.html
name_mapping = {
    'RGI60-11.00897': 'hef',
    'RGI60-11.01827': 'oberaletsch',
    'RGI60-01.10689': 'columbia',
    'RGI60-06.00477': 'iceland',
    'RGI60-05.10137': 'greenland',
    'RGI60-03.02489': 'devon',
    'RGI60-16.02207': 'shallap',
    'RGI60-19.02274': 'nordenskjoeld',
    'RGI60-19.00124': 'alexander',
    'RGI60-19.01251': 'gillock',
    'RGI60-03.00251': 'dobbin',
    'RGI60-15.02578': 'thana',
    'RGI60-07.01114': 'tellbreen',
    'RGI60-08.01126': 'nigards',
    'RGI60-18.00854': 'olivine',
    'RGI60-09.00552': 'lenin'
}
# create the comparison plots for each example glacier in the dictionary above
# and save them in their corresponding directory
for (rgiid, name) in name_mapping.items():
    output_path = path.abspath(path.join(os.getcwd(), '../../docs/_static/dems_examples/', name))
    pm.execute_notebook(
       'dem_comparison_for_rgitopo_docs.ipynb',
       '/dev/null',
       parameters = dict(rgi_id=rgiid, plot_dir=output_path)
    )