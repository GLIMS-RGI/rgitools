import geopandas as gpd
import shapely.geometry as shpg
from shapely.ops import linemerge
from salem import wgs84
from oggm.utils import haversine
from oggm.core.gis import _check_geometry


def compute_intersects(rgi_df):
    """Computes the intersection geometries between glaciers.

    The output is a shapefile with three columns:
    -  ``RGIId_1`` and ``RGIId_2``: the RGIIds of the two intersecting entities
    -  ``geometry``: the intersection geometry (LineString or MultiLineString)

    Parameters
    ----------
    rgi_df : geopandas.GeoDataFrame
        the RGI shapefile

    Returns
    -------
    a geopandas.GeoDataFrame
    """

    # clean geometries like OGGM does
    ngeos = []
    keep = []
    for g in rgi_df.geometry:
        try:
            g = _check_geometry(g)
            ngeos.append(g)
            keep.append(True)
        except:
            keep.append(False)
    gdf = rgi_df.loc[keep]
    gdf['geometry'] = ngeos

    out_cols = ['RGIId_1', 'RGIId_2', 'geometry']
    out = gpd.GeoDataFrame(columns=out_cols)

    for i, major in gdf.iterrows():

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
        except:
            gdfs = gdfs.loc[gdfs.intersects(major_poly.buffer(0))]

        for i, neighbor in gdfs.iterrows():

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
            except:
                # Anything can happen here but we should be more conservative
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

    out.crs = wgs84.srs

    return out
