import os
import shutil
import logging
from functools import wraps
import time
import tempfile
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely.geometry as shpg
from shapely.ops import linemerge
import networkx as nx
from salem import wgs84
from oggm.utils import haversine, compile_glacier_statistics
from shapely.geometry import mapping

# Interface
from oggm.utils import get_demo_file, mkdir   # noqa: F401


# Remove all previous handlers associated with the root logger object
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


# Recipe
# https://stackoverflow.com/questions/7003898/
# using-functools-wraps-with-a-logging-decorator
class CustomFormatter(logging.Formatter):
    """Overrides funcName with value of name_override if it exists"""
    def format(self, record):
        if hasattr(record, 'name_override'):
            record.funcName = record.name_override
        return super(CustomFormatter, self).format(record)


handler = logging.StreamHandler()
format = CustomFormatter('%(asctime)s: %(name)s.%(funcName)s: %(message)s',
                         datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(format)
logger = logging.getLogger(__name__)
logger.addHandler(handler)


def mappable_func(*args):
    """Wrapper to unpack kwargs and pass them to args[0]"""
    kwargs = dict(to_file=args[2], job_id=args[3])
    if len(args) == 6:
        # horrible workaround for compute hypsometries
        kwargs['set_oggm_params'] = args[4]
        kwargs['oggm_working_dir'] = args[5]
    return args[0](args[1], **kwargs)


def io_logger(func):
    """Decorator for common IO and logging logic."""

    @wraps(func)
    def wrapper(*args, **kwargs):

        job_id = kwargs.pop('job_id', '')
        if job_id:
            start_time = time.time()
            logger.info('Starting job %s ...' % job_id,
                        extra={'name_override': func.__name__})

        to_file = kwargs.get('to_file', '')
        if to_file:
            if os.path.exists(to_file):
                raise RuntimeError("Won't overwrite existing file: " +
                                   to_file)

        nargs = []
        for rgi_df in args:
            if isinstance(rgi_df, str):
                # A path to a file
                rgi_df = gpd.read_file(rgi_df)
            else:
                rgi_df = rgi_df.copy()
            nargs.append(rgi_df)

        out_file = func(*nargs, **kwargs)

        # Write and return -- only if expected output
        if isinstance(out_file, gpd.GeoDataFrame):
            out_file.crs = wgs84.srs
            if to_file:
                out_file.to_file(to_file)

        if job_id:
            m, s = divmod(time.time() - start_time, 60)
            logger.info('Job {} done in '
                        '{} m {} s!'.format(job_id, int(m), round(s)),
                        extra={'name_override': func.__name__})
        return out_file

    return wrapper


def _multi_to_poly(geometry, rid=''):
    """Sometimes an RGI geometry is a multipolygon: this should not happen.

    Parameters
    ----------
    geometry : shpg.Polygon or shpg.MultiPolygon
        the geometry to check
    rid : str, optional
        the glacier ID (for logging)

    Returns
    -------
    the corrected geometry
    """

    if 'Multi' in geometry.type:
        parts = np.array(geometry)
        for p in parts:
            assert p.type == 'Polygon'
        areas = np.array([p.area for p in parts])
        parts = parts[np.argsort(areas)][::-1]
        areas = areas[np.argsort(areas)][::-1]

        # First case (e.g. RGIV4):
        # let's assume that one poly is exterior and that
        # the other polygons are in fact interiors
        exterior = parts[0].exterior
        interiors = []
        was_interior = 0
        for p in parts[1:]:
            if parts[0].contains(p):
                interiors.append(p.exterior)
                was_interior += 1
        if was_interior > 0:
            # We are done here, good
            geometry = shpg.Polygon(exterior, interiors)
        else:
            # This happens for bad geometries. We keep the largest
            geometry = parts[0]
            if np.any(areas[1:] > (areas[0] / 4)):
                logger.warning('Geometry {} lost quite a chunk.'.format(rid))

    if geometry.type != 'Polygon':
        raise RuntimeError('Geometry {} is not a Polygon.'.format(rid))
    return geometry


@io_logger
def check_geometries(rgi_df, to_file='', job_id=''):
    """Checks and (when possible) corrects the RGI geometries.

    It adds a new column to the data: ``check_geom``, a str:
    - 'WARN:WasMultiPolygon' when the entity was a MultiPolygon instead of
      Polygon.
    - 'WARN:WasInvalid' when the entity wasn't valid but is now corrected.
    - 'ERR:isInvalid' when the entity isn't valid and cannot be corrected

    Parameters
    ----------
    rgi_df : str or geopandas.GeoDataFrame
        the RGI shapefile
    to_file : str, optional
        set to a valid path to write the file on disk
    job_id : str, optional
        if you want to log what happens, give a name to this job

    Returns
    -------
    a geopandas.GeoDataFrame
    """

    for i, s in rgi_df.iterrows():
        geometry = s.geometry
        rgi_df.loc[i, 'check_geom'] = ''
        if geometry.type != 'Polygon':
            geometry = _multi_to_poly(geometry, rid=s.RGIId)
            msg = 'WARN:WasMultiPolygon;'
            logger.debug('{}: '.format(s.RGIId) + msg)
            rgi_df.loc[i, 'check_geom'] = rgi_df.loc[i, 'check_geom'] + msg

        if not geometry.is_valid:
            geometry = geometry.buffer(0)
            if geometry.type != 'Polygon':
                raise RuntimeError('Geometry cannot be corrected: '
                                   '{}'.format(s.RGIId))
            msg = 'WARN:WasInvalid;' if geometry.is_valid else 'ERR:isInvalid'
            logger.debug('{}: '.format(s.RGIId) + msg)
            rgi_df.loc[i, 'check_geom'] = rgi_df.loc[i, 'check_geom'] + msg
        rgi_df.loc[i, 'geometry'] = geometry

    return rgi_df


@io_logger
def compute_intersects(rgi_df, to_file='', job_id=''):
    """Computes the intersection geometries between glaciers.

    The output is a shapefile with three columns:
    -  ``RGIId_1`` and ``RGIId_2``: the RGIIds of the two intersecting entities
    -  ``geometry``: the intersection geometry (LineString or MultiLineString)

    Parameters
    ----------
    rgi_df : str or geopandas.GeoDataFrame
        the RGI shapefile
    to_file : str, optional
        set to a valid path to write the file on disk
    job_id : str, optional
        if you want to log what happens, give a name to this job

    Returns
    -------
    a geopandas.GeoDataFrame
    """

    gdf = rgi_df.copy()
    out_cols = ['RGIId_1', 'RGIId_2', 'geometry']
    out = gpd.GeoDataFrame(columns=out_cols)
    for _, major in gdf.iterrows():

        # Exterior only
        major_poly = major.geometry.exterior

        # sort by distance to the current glacier
        gdf['dis'] = haversine(major.CenLon, major.CenLat,
                               gdf.CenLon, gdf.CenLat)
        gdfs = gdf.sort_values(by='dis')

        # Keep glaciers in which intersect
        gdfs = gdfs.loc[gdfs.dis < 200000]
        gdfs = gdfs.loc[gdfs.RGIId != major.RGIId]
        gdfs = gdfs.loc[gdfs.intersects(major_poly)]

        for _, neighbor in gdfs.iterrows():

            # Already computed?
            if neighbor.RGIId in out.RGIId_1 or neighbor.RGIId in out.RGIId_2:
                continue

            # Exterior only
            # Buffer is needed for numerical reasons
            # 1e-4 seems reasonable although it should be dependant on loc
            neighbor_poly = neighbor.geometry.exterior.buffer(1e-4)

            # Go
            mult_intersect = major_poly.intersection(neighbor_poly)

            # Handle the different kind of geometry output
            if isinstance(mult_intersect, shpg.Point):
                continue
            if isinstance(mult_intersect, shpg.linestring.LineString):
                mult_intersect = [mult_intersect]
            if len(mult_intersect) == 0:
                continue
            mult_intersect = [m for m in mult_intersect if
                              not isinstance(m, shpg.Point)]
            if len(mult_intersect) == 0:
                continue

            # Simplify the geometries if possible
            mult_intersect = linemerge(mult_intersect)

            # Add each line to the output file
            if isinstance(mult_intersect, shpg.linestring.LineString):
                mult_intersect = [mult_intersect]
            for line in mult_intersect:
                assert isinstance(line, shpg.linestring.LineString)
                # Filter the very small ones
                if line.length < 1e-3:
                    continue
                line = gpd.GeoDataFrame([[major.RGIId, neighbor.RGIId, line]],
                                        columns=out_cols)
                out = out.append(line)

    # Index and merge
    out.reset_index(inplace=True, drop=True)
    return out


def find_clusters(intersects_df):
    """Given a list of interlinked entities, find the glacier clusters.

    Parameters
    ----------
    intersects_df :  str or geopandas.GeoDataFrame
        the RGI intersects shapefile

    Returns
    -------
    a dict wchich keys are the first RGIId of the cluster and the values are
    the list of this cluster's RGIId's
    """

    if isinstance(intersects_df, str):
        intersects_df = gpd.read_file(intersects_df)

    # Make the clusters
    # https://en.wikipedia.org/wiki/Connected_component_%28graph_theory%29
    graph = nx.Graph()
    graph.add_edges_from(np.vstack((intersects_df.RGIId_1.values,
                                    intersects_df.RGIId_2.values)).T)

    # Convert to dict and sort
    out = dict()
    for c in nx.connected_components(graph):
        c = sorted(list(c))
        out[c[0]] = c
    return out


@io_logger
def merge_clusters(rgi_df, intersects_df, keep_all=True, to_file='',
                   job_id=''):
    """Selects the glacier clusters out of an RGI file and merges them.

    The output is an RGI shapefile with an additional column: ``OrigIds``,
    which contains a string of the cluster's original RGIIds, separated
    with a comma.

    Parameters
    ----------
    rgi_df : str or geopandas.GeoDataFrame
        the RGI shapefile
    intersects_df : str or geopandas.GeoDataFrame
        the RGI intersects shapefile
    keep_all : bool, default: True
        Whether to keep the single glaciers in the output shapefile as well
    to_file : str, optional
        set to a valid path to write the file on disk
    job_id : str, optional
        if you want to log what happens, give a name to this job

    Returns
    -------
    a geopandas.GeoDataFrame
    """

    # Find the clusters first
    clusters = find_clusters(intersects_df)

    # Add the clusters
    rgi_df['OrigIds'] = ''
    for k, c in clusters.items():
        if len(c) > 1:
            rgi_df.loc[rgi_df.RGIId.isin(c), 'OrigIds'] = ';'.join(c)

    # Add single glaciers
    if keep_all:
        d1 = rgi_df.loc[rgi_df.OrigIds == '']
    else:
        d1 = gpd.GeoDataFrame()

    # Compute the merged geometries
    rgi_df = rgi_df.loc[rgi_df.OrigIds != '']
    d2 = rgi_df.dissolve(by='OrigIds')

    # Process attributes
    gb = rgi_df[['OrigIds', 'Area', 'Zmax', 'Zmin']].groupby('OrigIds')
    d2['Area'] = gb.sum()['Area']
    d2['Zmax'] = gb.max()['Zmax']
    d2['Zmin'] = gb.min()['Zmin']
    centers = [g.centroid.xy for g in d2.geometry]
    d2['CenLat'] = [c[1][0] for c in centers]
    d2['CenLon'] = [c[0][0] for c in centers]

    # dummy index and merge
    d2.reset_index(inplace=True)
    out = pd.concat([d1, d2], sort=False)

    out = out.sort_values(by='RGIId')
    out.reset_index(drop=True)

    return out


def _feature(ind, rowobj):
    return {
        'id': str(ind),
        'type': 'Feature',
        'properties':
            dict((k, v) for k, v in rowobj.items() if k != 'geometry'),
        'geometry': mapping(rowobj['geometry'])}


@io_logger
def hypsometries(rgi_df, to_file='', job_id='', oggm_working_dir='',
                 set_oggm_params=None):
    """
    Create hypsometries for glacier geometries using the best available DEM.

    We use the same convention as documented in RGIV6: bins of size 50,
    from 0 m a.s.l. to max elevation in 50 m bins.

    The DEM choice and grid resolution is managed by OGGM.

    Parameters
    ----------
    rgi_df : str or geopandas.GeoDataFrame
        the RGI shapefile
    to_file : str, optional
        set to a valid path to write the file on disk
        For this task: the file name should have no ending, as two files
        are written to disk
    job_id : str, optional
        if you want to log what happens, give a name to this job
    oggm_working_dir: str, optional
        path to the folder where oggm will write its GlacierDirectories.
        Default is to use a temporary folder (not recommended)
    set_oggm_params : callable, optional
        a function which sets the desired OGGM parameters
    """

    if to_file:
        _, ext = os.path.splitext(to_file)
        if ext != '':
            raise ValueError('to_file should not have an extension!')
        if os.path.exists(to_file + '.csv'):
            raise RuntimeError("Won't overwrite existing file: " +
                               to_file + '.csv')
        if os.path.exists(to_file + '.shp'):
            raise RuntimeError("Won't overwrite existing file: " +
                               to_file + '.shp')

    from oggm import cfg, workflow, tasks
    cfg.initialize()

    if set_oggm_params is not None:
        set_oggm_params(cfg)

    del_dir = False
    if not oggm_working_dir:
        del_dir = True
        oggm_working_dir = tempfile.mkdtemp()
    cfg.PATHS['working_dir'] = oggm_working_dir

    # Get the DEM job done by OGGM
    cfg.PARAMS['use_intersects'] = False
    cfg.PARAMS['continue_on_error'] = True
    cfg.PARAMS['use_multiprocessing'] = False
    gdirs = workflow.init_glacier_directories(rgi_df)
    workflow.execute_entity_task(tasks.define_glacier_region, gdirs)
    workflow.execute_entity_task(tasks.simple_glacier_masks, gdirs,
                                 write_hypsometry=True)
    compile_glacier_statistics(gdirs,
                               filesuffix='_{}'.format(gdirs[0].rgi_region))

    out_gdf = rgi_df.copy().set_index('RGIId')
    try:
        is_nominal = np.array([int(s[0]) == 2 for s in out_gdf.RGIFlag])
    except AttributeError:
        is_nominal = np.array([int(s) == 2 for s in out_gdf.Status])
    cols = ['Zmed', 'Zmin', 'Zmax', 'Slope', 'Aspect']
    out_gdf.loc[~is_nominal, cols] = np.NaN

    df = pd.DataFrame()
    for gdir in gdirs:

        rid = gdir.rgi_id
        df.loc[rid, 'RGIId'] = gdir.rgi_id
        df.loc[rid, 'GLIMSId'] = gdir.glims_id
        df.loc[rid, 'Area'] = gdir.rgi_area_km2

        if not gdir.has_file('hypsometry') or gdir.is_nominal:
            continue

        idf = pd.read_csv(gdir.get_filepath('hypsometry')).iloc[0]
        for c in idf.index:
            try:
                int(c)
            except ValueError:
                continue
            df.loc[rid, c] = idf[c]

        out_gdf.loc[rid, 'Zmed'] = idf.loc['Zmed']
        out_gdf.loc[rid, 'Zmin'] = idf.loc['Zmin']
        out_gdf.loc[rid, 'Zmax'] = idf.loc['Zmax']
        out_gdf.loc[rid, 'Slope'] = idf.loc['Slope']
        out_gdf.loc[rid, 'Aspect'] = idf.loc['Aspect']

    out_gdf = out_gdf.reset_index()
    df = df.reset_index(drop=True)
    bdf = df[df.columns[3:]].fillna(0).astype(np.int)
    ok = bdf.sum(axis=1)
    bdf.loc[ok < 1000, :] = -9
    df[df.columns[3:]] = bdf

    # Sort columns
    df = df[np.append(df.columns[:3], sorted(df.columns[3:]))]

    if del_dir:
        shutil.rmtree(oggm_working_dir)

    # replace io write
    if to_file:
        out_gdf.crs = wgs84.srs
        out_gdf.to_file(to_file + '.shp')
        df.to_csv(to_file + '_hypso.csv', index=False)

    return df, out_gdf.reset_index()
