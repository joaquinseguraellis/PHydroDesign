"""

"""

# Libraries

import shapefile
import shapely
import rasterio
import rasterio.mask
import scipy

import numpy as np

# Functions

def shp_mask(
        raster, transform, shp_path,
):
    """
    Applies a mask to raster data based in a shape file.
    """
    with shapefile.Reader(shp_path) as shp_file:
        geom = shapely.geometry.shape(shp_file.shape(0).__geo_interface__)
    with rasterio.io.MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff',
            height=raster.shape[0],
            width=raster.shape[1],
            count=1,
            dtype=raster.dtype,
            transform=transform,
        ) as dataset:
            dataset.write(raster, 1)
        with memfile.open() as dataset:
            output, _ = rasterio.mask.mask(dataset, [geom], nodata=np.nan)
    return output.squeeze(0)
    
def fill_interp(
        lon, lat, data, mask=None,
):
    """
    
    """
    if mask is not None:
        data[mask] = np.nan
    X, Y = np.meshgrid(lon, lat)
    points = np.array([X.flatten(), Y.flatten()]).T
    data = data.flatten()
    points = points[~np.isnan(data)]
    data = data[~np.isnan(data)]
    return scipy.interpolate.griddata(
        points, data, (X, Y), method='linear',
    )

# Classes