import logging
import time
import geopandas as gpd
import shapely.geometry as shpg
from shapely.ops import linemerge
from salem import wgs84
from oggm.utils import haversine
from oggm.core.gis import _check_geometry

# Module logger
logging.basicConfig(format='%(asctime)s: %(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)


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
        logger.info('Starting job %s ...' % job_id)

    if isinstance(rgi_df, str):
        # A path to a file
        rgi_df = gpd.read_file(rgi_df)

    # clean geometries like OGGM does
    ngeos = []
    keep = []
    for g in rgi_df.geometry:
        try:
            g = _check_geometry(g)
            ngeos.append(g)
            keep.append(True)
        except RuntimeError:
            keep.append(False)
    gdf = rgi_df.loc[keep]
    gdf['geometry'] = ngeos

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
        try:
            gdfs = gdfs.loc[gdfs.intersects(major_poly)]
        except RuntimeError:
            gdfs = gdfs.loc[gdfs.intersects(major_poly.buffer(0))]

        for _, neighbor in gdfs.iterrows():

            # Already computed?
            if neighbor.RGIId in out.RGIId_1 or neighbor.RGIId in out.RGIId_2:
                continue

            # Exterior only
            # Buffer is needed for numerical reasons
            # 1e-4 seems reasonable although it should be dependant on loc
            neighbor_poly = neighbor.geometry.exterior.buffer(1e-4)

            # Go
            try:
                mult_intersect = major_poly.intersection(neighbor_poly)
            except RuntimeError:
                continue

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
        logger.info('Job {} done in {} m {} s!'.format(job_id, int(m),
                                                       round(s)))
    return out
