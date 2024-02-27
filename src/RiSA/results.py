"""
This module gives the result of the analysis.
"""

# Dependencies

MODULES = ['pyshp', 'shapely', 'rasterio', 'scipy']
import pip
for module in MODULES:
    pip.main(['install', module])
del pip

# Libraries

import pickle
import pkg_resources

from .masks import *
from .interp import *

# Global variables

ARG_SHP_PATH = pkg_resources.resource_filename('RiSA', 'data/shp/argentina.shp')

# Functions

def open_results(
        path,
):
    """
    
    """
    with open(path, 'rb') as f:
        data_dict = pickle.load(f)
    return data_dict

def loc_validation(
        lon, lat, shp_path,
):
    """
    
    """
    with shapefile.Reader(shp_path) as shp_file:
        geom = shapely.geometry.shape(shp_file.shape(0).__geo_interface__)
    return geom.contains(shapely.geometry.Point(lon, lat))

def get_design_rainfall(
        product, T, lon, lat,
        shp_path=ARG_SHP_PATH,
):
    """
    
    """
    result = {
        'longitude': lon,
        'latitude': lat,
        'in Arg': loc_validation(lon, lat, shp_path),
        'Return period': T,
    }
    data_dict = open_results(
        pkg_resources.resource_filename('RiSA', f'data/imerg_{product}.risa'),
    )
    if product == 'Final':
        power = 3
    else:
        power = 2
    idw = IDW_Grid_Interpolation(data_dict['lon'], data_dict['lat'], lon, lat, power)
    l = data_dict['T'] == T
    for k, key_ in enumerate(['Lower limit', 'Estimate', 'Higher limit']):
        prec = data_dict[product][:, :, k, l].T
        prec = fill_interp(
            data_dict['lon'], data_dict['lat'],
            prec[0], ~data_dict[f'{product}_tests'],
        )
        if shp_path is not None:
            prec = shp_mask(
                prec,
                rasterio.transform.Affine(
                    0.1, 0, data_dict['lon'][0], 0, 0.1, data_dict['lat'][0],
                ),
                shp_path,
            )
        result[key_] = idw.interp(np.array([prec]))[0]
    return result