import logging
import time
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely.geometry as shpg
from shapely.ops import linemerge
from salem import wgs84
from oggm.utils import haversine, get_demo_file, mkdir   # noqa: F401

# Remove all previous handlers associated with the root logger object
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s: %(name)s.%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)


def _multi_to_poly(geometry, rid=''):
    """Sometimes an RGI geometry is a multipolygon: this should not happen.

    Parameters
    ----------
    geometry : shpg.Polygon or shpg.MultiPolygon
        the geometry to check
    rid : str, optional
        the glacie ID (for logging)

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

    if job_id:
        start_time = time.time()
        logger.info('Starting job %s ...' % job_id)

    if isinstance(rgi_df, str):
        # A path to a file
        rgi_df = gpd.read_file(rgi_df)
    else:
        rgi_df = rgi_df.copy()

    for i, s in rgi_df.iterrows():
        geometry = s.geometry
        rgi_df.loc[i, 'check_geom'] = ''
        if geometry.type != 'Polygon':
            geometry = _multi_to_poly(geometry, rid=s.RGIId)
            msg = 'WARN:WasMultiPolygon;'
            rgi_df.loc[i, 'check_geom'] = rgi_df.loc[i, 'check_geom'] + msg

        if not geometry.is_valid:
            geometry = geometry.buffer(0)
            if geometry.type != 'Polygon':
                raise RuntimeError('Geometry cannot be corrected: '
                                   '{}'.format(s.RGIId))
            msg = 'WARN:WasInvalid;' if geometry.is_valid else 'ERR:isInvalid'
            rgi_df.loc[i, 'check_geom'] = rgi_df.loc[i, 'check_geom'] + msg
        rgi_df.loc[i, 'geometry'] = geometry

    # Write and return
    if to_file:
        rgi_df.to_file(to_file)

    if job_id:
        m, s = divmod(time.time() - start_time, 60)
        logger.info('Job {} done in '
                    '{} m {} s!'.format(job_id, int(m), round(s)))
    return rgi_df


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

    if job_id:
        start_time = time.time()
        logger.info('Starting compute_intersects job %s ...' % job_id)

    if isinstance(rgi_df, str):
        # A path to a file
        rgi_df = gpd.read_file(rgi_df)

    gdf = rgi_df.copy()
    out_cols = ['RGIId_1', 'RGIId_2', 'geometry']
    out = gpd.GeoDataFrame(columns=out_cols)
    for _, major in gdf.iterrows():

        # Exterior only
        major_poly = major.geometry.exterior

        # sort by distance to the current glacier
        gdf['dis'] = haversine(major.CenLon, major.CenLat,
                               gdf.CenLon, gdf.CenLat)
        gdfs = gdf.sort_values(by='dis').iloc[1:]

        # Keep glaciers in which intersect
        gdfs = gdfs.loc[gdfs.dis < 200000]
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
                line = gpd.GeoDataFrame([[major.RGIId, neighbor.RGIId, line]],
                                        columns=out_cols)
                out = out.append(line)

    # Write and return
    out.crs = wgs84.srs
    if to_file:
        out.to_file(to_file)

    if job_id:
        m, s = divmod(time.time() - start_time, 60)
        logger.info('compute_intersects job {} done in '
                    '{} m {} s!'.format(job_id, int(m), round(s)))
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
    l = np.vstack((intersects_df.RGIId_1.values,
                   intersects_df.RGIId_2.values)).T
    clusters = []
    while len(l) > 0:
        n = l[0]
        c = set(n)
        found_one = True
        while found_one:
            found_one = False
            remove = []
            for i, ni in enumerate(l):
                if ni[0] in c or ni[1] in c:
                    c.update(ni)
                    remove = np.append(remove, i)
                    found_one = True
            l = np.delete(l, remove, axis=0)
        clusters.append(c)

    # Convert to dict and sort
    out = dict()
    for c in clusters:
        c = sorted(list(c))
        out[c[0]] = c
    return out


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

    if job_id:
        start_time = time.time()
        logger.info('Starting job %s ...' % job_id)

    if isinstance(rgi_df, str):
        rgi_df = gpd.read_file(rgi_df)
    else:
        rgi_df = rgi_df.copy()
    if isinstance(intersects_df, str):
        intersects_df = gpd.read_file(intersects_df)

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
    gb = rgi_df.groupby('OrigIds')
    d2['Area'] = gb.sum()['Area']
    d2['Zmax'] = gb.max()['Zmax']
    d2['Zmin'] = gb.min()['Zmin']
    centers = [g.centroid.xy for g in d2.geometry]
    d2['CenLat'] = [c[1][0] for c in centers]
    d2['CenLon'] = [c[0][0] for c in centers]

    # dummy index and merge
    d2.reset_index(inplace=True)
    out = pd.concat([d1, d2])

    out = out.sort_values(by='RGIId')
    out.reset_index(drop=True)

    out.crs = wgs84.srs
    if to_file:
        out.to_file(to_file)

    if job_id:
        m, s = divmod(time.time() - start_time, 60)
        logger.info('Job {} done in {} m {} s!'.format(job_id, int(m),
                                                       round(s)))
    return out
