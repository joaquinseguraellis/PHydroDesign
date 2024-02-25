"""
This module contains functions and clases for managing geographically distributed gridded data.
"""

# Libraries

import pykrige
import shapefile
import rasterio

import matplotlib.patches as mpatches
import shapely.geometry
import rasterio.mask
import rasterio.transform
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.io.img_tiles

from global_land_mask import globe
from osgeo import gdal
from osgeo import ogr

from .libraries import *
from .hydro_tools import *
from .frequency_analysis import *

# Functions

def cut(
        data, x, y, bbox,
):
    """
    Cut a numpy.array to a bbox.

    Parameters
    ----------
    data : 2-D ndarray with shape (X, Y).
        The data to cut.
    x, y : 1-D ndarray with floats of shape (X,) and (Y,) each.
        x and y coordinates.
    bbox : 1-D ndarray or list of shape (4,).
        bbox[0] : float.
            x low limit.
        bbox[1] : float.
            x high limit.
        bbox[2] : float.
            y low limit.
        bbox[3] : float.
            y high limit.

    Returns
    -------
    data : 2-D ndarray with shape (X_, Y_).
        The result of cutting data.
    x, y : 1-D ndarray with floats of shape (X,) and (Y,) each.
        The result of cutting x and y coordinates.

    Examples
    --------
    Suppose we have the 2-D narray data

    >>> import numpy as np

    >>> data = np.random.random((100, 200))
    >>> print('data shape =', data.shape)

    that has x and y coordinates

    >>> x = np.arange(800, 900)
    >>> y = np.arange(100, 300)
    >>> print('x shape =', x.shape)
    >>> print('y shape =', y.shape)
    
    and we want to cut it to the bbox list

    >>> bbox = [810, 890, 120, 250]

    we can apply the "cut" function to do it.

    >>> new_data = cut(data, x, y, bbox)
    >>> print('new_data shape =', new_data.shape)
    >>> print('x shape =', x.shape)
    >>> print('y shape =', y.shape)

    """
    data = data[x >= bbox[0], :]
    x = x[x >= bbox[0]]
    data = data[x <= bbox[1], :]
    x = x[x <= bbox[1]]
    data = data[:, y >= bbox[2]]
    y = y[y >= bbox[2]]
    data = data[:, y <= bbox[3]]
    y = y[y <= bbox[3]]
    return data, x, y

def etopo(
        lon_new, lat_new, earth_data_path, engine='netcdf4',
):
    """
    Return topography for a define longitud and latitud
    """
    if 'ETOPO1_Bed_g_gdal.grd' in os.listdir(earth_data_path):
        ds = xr.open_dataset(
            Path(earth_data_path, 'ETOPO1_Bed_g_gdal.grd'), engine=engine,
        )
    else:
        url = 'https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/grid_registered/netcdf/ETOPO1_Bed_g_gdal.grd.gz'
        result = requests.get(url)
        result.raise_for_status()
        f = open(Path(earth_data_path, 'ETOPO1_Bed_g_gdal.grd'),'wb')
        f.write(result.content)
        f.close()
        ds = xr.open_dataset(
            Path(earth_data_path, 'ETOPO1_Bed_g_gdal.grd'), engine=engine,
        )
    lon_range  = ds['x_range'].values
    lat_range  = ds['y_range'].values
    topo_range = ds['z_range'].values
    spacing    = ds['spacing'].values
    dimension  = ds['dimension'].values
    z          = ds['z'].values
    lon = np.arange(
        lon_range[0], lon_range[1]+1/10000,
        (lon_range[1]-lon_range[0])/(dimension[0]-1),
    )
    lon = np.where(lon > 180, 180, lon)
    lat = np.arange(
        lat_range[0], lat_range[1]+1/10000,
        (lat_range[1]-lat_range[0])/(dimension[1]-1),
    )
    lat = np.where(lat > 90, 90, lat)
    topo = np.flip(np.reshape(z, (dimension[1], dimension[0])), axis=0)
    interpolation = scipy.interpolate.interp2d(lon, lat, topo)
    lon_grid, lat_grid = np.meshgrid(lon_new, lat_new)
    return (
        np.where(
            globe.is_ocean(lat_grid, lon_grid), np.nan,
            interpolation(lon_new, lat_new)
        ),
        interpolation,
    )

def search_loc(
        lons_, lats_, lons, lats,
):
    """
    Search for nearest coordinates from lons and lats to lons_ and lats_.
    Return a numpy.array with the index where to find those coordinates.
    """
    lons  = np.sort(lons)
    lats  = np.sort(lats)
    low_lons  = np.searchsorted(lons, lons_)-1
    high_lons = np.searchsorted(lons, lons_)
    low_lats  = np.searchsorted(lats, lats_)-1
    high_lats = np.searchsorted(lats, lats_)
    return np.array([low_lons, high_lons, low_lats, high_lats])

def inside_bbox(
        bbox, y, x,
):
    """
    Wheter or not a point is inside a square bbox limits.

    Parameters:

        - bbox : dtype=list, tuple or numpy.array.
            bbox[3] and bbox[2] are higher and lower "y" limits. bbox[1] and bbox[0] are higher and lower "x" limits.
        - y, x : coordinates, dtype=float or int.

    Returns:

        - bool : True if point (x, y) is inside square bbox limits.
    """
    return y < bbox[3] and y > bbox[2] and x < bbox[1] and x > bbox[0]

def open_Catalini(
        path,
):
    """
    
    """
    dataset = gdal.Open(path, gdal.GA_ReadOnly)
    geotransform = dataset.GetGeoTransform()
    x = np.sort([
        geotransform[0] + geotransform[1] * i
            for i in range(dataset.RasterXSize)
    ])
    y = np.sort([
        geotransform[3] + geotransform[5] * i
            for i in range(dataset.RasterYSize)
    ])
    band = dataset.GetRasterBand(1)
    Z = np.flip(band.ReadAsArray(), axis=0).astype(float)
    Z[~(Z > 0)] = np.nan
    dataset = None
    band = None
    return x, y, Z

def open_stations_Catalini(
        path,
    ):
    """
    
    """
    shapefile = ogr.Open(str(path))
    layer = shapefile.GetLayer()
    data = [feature.items() for feature in layer]
    error = np.ones((len(data))).astype(bool)
    for i, p in enumerate(data):
        for k in ['Longitud O', 'Latitud S', 'Altitud']:
            try:
                p[k] = float(p[k])
            except:
                error[i] = False
    return (
        np.array([p['Longitud O'] for p in data])[error],
        np.array([p['Latitud S'] for p in data])[error],
    )

def get_imerg_dataset(
        path, bbox,
):
    """
    
    """
    try:
        with h5py.File(path, 'r') as hdf_file:
            keys = list(hdf_file.keys())
            del keys[keys.index('lat')]
            del keys[keys.index('lon')]
            del keys[keys.index('time')]
            data = dict()
            data['data'] = dict()
            for k in keys:
                aux = hdf_file[k][0] # mm/h
                aux[aux < 0] = np.nan
                aux, data['lon'], data['lat'] = cut(
                    aux, hdf_file['lon'][:], hdf_file['lat'][:], bbox,
                )
                data['data'][k] = np.array([aux / 2]) # mm
            data['time'] = np.array([datetime.datetime.strptime(
                hdf_file['time'].attrs['units'].decode('utf-8')[14:],
                '%Y-%m-%d %H:%M:%S %Z',
            ) + datetime.timedelta(seconds=int(hdf_file['time'][0]))])
        return data
    except Exception as e:
        print(path)
        print(e)
        raise

def get_imerg_daily_sum(
        file_paths, bbox,
):
    """
    
    """
    precipitationCal = list()
    precipitationUncal = list()
    IRprecipitation = list()
    HQprecipitation = list()
    for _ in tqdm(file_paths):
        data = [get_imerg_dataset(file_path, bbox) for file_path in _]
        precipitationCal.append(
            np.nansum(
                [data_['data']['precipitationCal'] for data_ in data],
                axis=0,
            )
        )
        precipitationUncal.append(
            np.nansum(
                [data_['data']['precipitationUncal'] for data_ in data],
                axis=0,
            )
        )
        IRprecipitation.append(
            np.nansum(
                [data_['data']['IRprecipitation'] for data_ in data],
                axis=0,
            )
        )
        HQprecipitation.append(
            np.nansum(
                [data_['data']['HQprecipitation'] for data_ in data],
                axis=0,
            )
        )
    return (
        np.concatenate(precipitationCal, axis=0),
        np.concatenate(precipitationUncal, axis=0),
        np.concatenate(IRprecipitation, axis=0),
        np.concatenate(HQprecipitation, axis=0),
    )

def get_imerg_grid(
        imerg_path, bin_path, T: list,
        dt_lims: list=[None, None],
        save: bool=True, analyze: bool=True,
):
    """
    This function opens imerg grid data, applies frequency analysis and saves it to a binary file.
    """
    def _open(path):
        bbox = [-76.05, -53.05, -55.95, -21.05] # lat1, lat2, lon1, lon2
        with h5py.File(path, 'r') as hdf_file:
            imerg_time = np.array(
                [
                    (
                        datetime.datetime.strptime(
                            str(hdf_file['time'].attrs['first_time']),
                            '%Y-%m-%d %H:%M:%S',
                        ) + datetime.timedelta(days=int(i))
                    ).replace(hour=0, minute=0, second=0)
                for i in hdf_file['time']]
            )
            lon = np.round(hdf_file['lon'][:], 2)
            lat = np.round(hdf_file['lat'][:], 2)
            imerg_data = hdf_file['precipitationCal'][:]
        __ = [cut(_, lon, lat, bbox) for _ in imerg_data]
        lon, lat = __[0][1:]
        imerg_data = np.array([_[0] for _ in __])
        return imerg_data, imerg_time, lon, lat
    
    def grid_indices(imerg_grid: Rainfall_Indices):
        imerg_grid = copy.deepcopy(imerg_grid)
        k1 = 'Y_rx1day'
        k2 = 'Y_3_sorted_rx1day'
        years = np.unique([_.year for _ in imerg_grid.time])[:-1]
        t = np.array([datetime.datetime(_, 1, 1) for _ in years])
        max_t = years.shape[0]
        rx1 = np.zeros(
            [max_t] + list(imerg_grid.result[k1]['data'].shape[1:]),
        )
        srx1 = np.zeros(
            [max_t] + list(imerg_grid.result[k2]['data'].shape[1:]),
        )
        cond = imerg_grid.start_month == 1
        _, index1, _ = np.intersect1d(
            years,
            np.array([_.year for _ in imerg_grid.result[k1]['time']]),
            return_indices=True,
        )
        rx1[index1] += imerg_grid.result[k1]['data'] * cond
        srx1[index1] += imerg_grid.result[k2]['data'] * cond
        for sm in range(2, 13):
            cond = imerg_grid.start_month == sm
            indices = Rainfall_Indices(
                imerg_grid.time, imerg_grid.data, start_month=sm,
            )
            indices.rxDday_calc(1)
            indices.sorted_max_calc()
            _, index1, _ = np.intersect1d(
                years,
                np.array([_.year for _ in indices.result[k1]['time']]),
                return_indices=True,
            )
            rx1[index1] += indices.result[k1]['data'] * cond
            srx1[index1] += indices.result[k2]['data'] * cond
        rx1[rx1 == 0] = np.nan
        srx1[srx1 == 0] = np.nan
        imerg_grid.result[k1]['time'] = t
        imerg_grid.result[k2]['time'] = t
        imerg_grid.result[k1]['data'] = rx1
        imerg_grid.result[k2]['data'] = srx1
        return imerg_grid
    
    if not os.path.exists(bin_path):
        files = os.listdir(imerg_path)
        imerg_grid, imerg_time, lon, lat = _open(Path(imerg_path, files[0]))
        for imerg_file in tqdm(files[1:]):
            imerg_data_, t, _, _ = _open(Path(imerg_path, imerg_file))
            imerg_time = np.concatenate([imerg_time, t])
            imerg_grid = np.concatenate([imerg_grid, imerg_data_], axis=0)
        imerg_grid = imerg_grid[np.argsort(imerg_time)]
        imerg_time = imerg_time[np.argsort(imerg_time)]
        if dt_lims[1] is not None:
            imerg_grid = imerg_grid[imerg_time < dt_lims[1]]
            imerg_time = imerg_time[imerg_time < dt_lims[1]]
        if dt_lims[0] is not None:
            imerg_grid = imerg_grid[imerg_time >= dt_lims[0]]
            imerg_time = imerg_time[imerg_time >= dt_lims[0]]
        imerg_grid = Rainfall_Indices(imerg_time, imerg_grid, start_month=1)
        imerg_grid.lon = lon
        imerg_grid.lat = lat
        if analyze:
            imerg_grid.rxDday_calc(1)
            imerg_grid.sorted_max_calc()
            sm = Rain_Gauge.detect_start_month(
                imerg_grid.time, imerg_grid.data,
            )
            imerg_grid.start_month = sm
            imerg_grid = grid_indices(imerg_grid)
            k_ = 'Y_rx1day'
            k_wo = 'data_without_outliers'
            imerg_grid.result[k_][k_wo] = copy.deepcopy(
                imerg_grid.result[k_]['data']
            )
            for i in range(imerg_grid.result[k_][k_wo].shape[1]):
                for j in range(imerg_grid.result[k_][k_wo].shape[2]):
                    imerg_grid.result[k_][k_wo][:, i, j] = Statictical_Tests.outliers_bulletin17b(
                        imerg_grid.result['Y_3_sorted_rx1day']['data'][:, :, i, j], 1
                    )[k_wo][-1]
            tests = Statictical_Tests(imerg_grid.result[k_][k_wo])
            tests.calculate()
            imerg_grid.result[k_][f'tests_{k_wo}'] = tests.result
            tests = Statictical_Tests(imerg_grid.result[k_]['data'])
            tests.calculate()
            imerg_grid.result[k_]['tests_data'] = tests.result
            imerg_grid.result[k_]['lognorm'] = np.full(
                (
                    imerg_grid.result[k_][k_wo].shape[1],
                    imerg_grid.result[k_][k_wo].shape[2],
                    3, len(T),
                ), np.nan
            )
            for i in range(imerg_grid.result[k_][k_wo].shape[1]):
                for j in range(imerg_grid.result[k_][k_wo].shape[2]):
                    ln = LogNormal_MV(imerg_grid.result[k_][k_wo][:, i, j])
                    imerg_grid.result[k_]['lognorm'][i, j] = ln.ppf(T)
            mean = np.nanmean(imerg_grid.result[k_]['data'], axis=0)
            std = np.nanstd(imerg_grid.result[k_]['data'], axis=0)
            imerg_grid.result[k_]['mean'] = mean
            imerg_grid.result[k_]['std'] = std
            imerg_grid.result[k_]['phi_pmp'] = 5.2253 * np.exp(
                1.958 * std / mean
            )
            imerg_grid.result[k_]['pmp'] = mean + std * imerg_grid.result[k_]['phi_pmp']
        if save:
            imerg_grid.save(bin_path)
    else:
        imerg_grid = Rainfall_Indices()
        imerg_grid.load(bin_path)
    return imerg_grid

def kriging_interp_to_grid(
        x, y, z, x_grid, y_grid, variogram_model,
):
    """
    This function interpolates using Universal Kriging
    """
    uk = pykrige.uk.UniversalKriging(
        x, y, z, variogram_model=variogram_model,
    )
    return uk.execute('grid', x_grid, y_grid)[0]

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

def get_kriging_prec(
        lon, lat, lon_grid, lat_grid, prec,
        shp_path=None, elevation_mask=None,
):
    """
    Get Kriging interpolation and masks it to elevation mask and shape file.
    """
    prec_interp = kriging_interp_to_grid(
        lon, lat, prec, lon_grid, lat_grid, 'spherical',
    )
    if shp_path is not None:
        prec_interp = shp_mask(
            prec_interp,
            rasterio.transform.Affine(
                0.1, 0, lon_grid[0], 0, 0.1, lat_grid[0]
            ),
            shp_path,
        )
    if elevation_mask is not None:
        return np.ma.masked_array(prec_interp, elevation_mask)
    else:
        return prec_interp
    
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

class Map:
    """
    Basemap
    """

    projection_crs = ccrs.PlateCarree()

    def __init__(self, bbox, fontsize=12):
        self.bbox = bbox
        self.width = self.bbox[3] - self.bbox[1]
        self.height = self.bbox[2] - self.bbox[0]
        self.fs = fontsize

    def create_figure(self, title=None, figsize=None, dpi=300):
        if figsize is None:
            scale_factor = 10 / np.max([self.width, self.height])
            figsize = (self.width * scale_factor, self.height * scale_factor)
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        if title is not None:
            self.fig.suptitle(title, fontsize=self.fs+2)
        self.ax = self.fig.add_subplot(
            1, 1, 1, projection=self.projection_crs,
        )

    def create_north_arrow(self, ax, x=None, y=None):
        width = self.width * 0.01
        height = self.height * 0.05
        head_width = width * 2.5
        head_length = height * 0.3
        if x is None:
            x = self.width * 0.82 + self.bbox[1]
        if y is None:
            y = self.height * 0.10 + self.bbox[0]
        ax.add_patch(mpatches.FancyArrow(
            x, y, 0, height, width=width, head_width=head_width,
            head_length=head_length, length_includes_head=True,
            color='black',
        ))
        ax.text(
            x, y - head_width * 0.20, 'N', c='#000000',
            fontsize=self.fs + 4, stretch='condensed', weight='bold',
            ha='center', va='top',
        )

    def set_map(self, ax, df=0):
        ax.set_extent([
            self.bbox[1] - df, self.bbox[3] + df,
            self.bbox[0] - df, self.bbox[2] + df,
        ], crs=self.projection_crs)
        grid_step = np.min([int(self.width / 5), int(self.height / 5)])
        gl = ax.gridlines(
            draw_labels=True, linewidth=0.5,
            linestyle='--', alpha=0.7, dms=True,
            xlocs=np.arange(
                int(self.bbox[1] - df), int(self.bbox[3] + df), grid_step
            ),
            ylocs=np.arange(
                int(self.bbox[0] - df), int(self.bbox[2] + df), grid_step
            ),
        )
        gl.xlabel_style = {'size': self.fs}
        gl.ylabel_style = {'size': self.fs}

    def draw_limits(
            self, ax, countries_shp_path=None,
            provinces_shp_path=None,
            departments_shp_path=None,
        ):
        if countries_shp_path is not None:
            countries = list(
                shpreader.Reader(countries_shp_path).geometries()
            )
            ax.add_geometries(
                countries, self.projection_crs, edgecolor='black',
                facecolor='none', linewidth=0.5, linestyle='-',
            )
        if provinces_shp_path is not None:
            provinces = list(
                shpreader.Reader(provinces_shp_path).geometries()
            )
            ax.add_geometries(
                provinces, self.projection_crs, edgecolor='black',
                facecolor='none', linewidth=0.2, linestyle=(10, (10, 10)),
            )
        if departments_shp_path is not None:
            departments = list(
                shpreader.Reader(departments_shp_path).geometries()
            )
            ax.add_geometries(
                departments, self.projection_crs, edgecolor='black',
                facecolor='none', linewidth=0.2, linestyle='-.',
            )

class IDW_Grid_Interpolation:
    """
    Inverse distance weighting interpolation for regular gridded data.
    Initiate the class with:
    - x, y (1D numpy.array or list): coordinates of gridded data.
    - x_, y_ (int or float): coordinates where interpolation is needed.
    - power (int or float): power for the equation, 1 and 2 are usually used.
    https://en.wikipedia.org/wiki/Inverse_distance_weighting
    """

    def __init__(self, x, y, x_, y_, power):
        self.x, self.y = x, y
        self.p = (x_, y_)
        x, y = np.meshgrid(self.x, self.y)
        self.get_d(x, y, x_, y_)
        self.get_w(power)

    def get_d(self, x, y, x_, y_):
        """
        
        """
        self.d = ((x - x_)**2 + (y - y_)**2)**0.5

    def get_w(self, power):
        """
        
        """
        self.w = self.d**-power

    def get_u(self, u):
        """
        
        """
        if np.any(self.tolerance):
            return u[self.tolerance][0]
        else:
            w = copy.deepcopy(self.w)
            w[np.isnan(u)] = np.nan
            return np.nansum(w * u) / np.nansum(w)
    
    def interp(self, grid_data, tolerance=0.001, axes=None):
        """
        
        """
        self.tolerance = self.d <= tolerance
        if axes is not None:
            grid_data = np.transpose(grid_data, axes)
        return np.array([self.get_u(_) for _ in grid_data])

class RegularGridInterpolator:
    """
    
    """

    def __init__(self, points, values, method) -> None:
        self.interps = np.array([
            scipy.interpolate.RegularGridInterpolator(points, _, method)
                for _ in values
        ])
    
    def interp(self, x, y):
        """
        
        """
        return np.array([_([x, y])[0] for _ in self.interps])
    
class Card(Map):
    """
    Create a card with station information.
    """

    def __init__(self, bbox, fontsize, station, save_path):
        super().__init__(bbox, fontsize)
        self.bbox = bbox
        self.station = station
        self.save_path = save_path
        self.width = self.bbox[3] - self.bbox[1]
        self.height = self.bbox[2] - self.bbox[0]
        self.fs = fontsize

    def create_figure(self, title=None, figsize=None, dpi=300):
        if figsize is None:
            scale_factor = 10 / np.max([self.width, self.height])
            figsize = (
                3 * self.width * scale_factor, self.height * scale_factor,
            )
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        if title is not None:
            self.fig.suptitle(title, fontsize=self.fs+2)
        self.ax_info = self.fig.add_subplot(1, 3, 1)
        self.ax_plot1 = self.fig.add_subplot(2, 3, 2)
        self.ax_plot2 = self.fig.add_subplot(2, 3, 5)
        self.ax_plot1.sharex(self.ax_plot2)
        self.ax_map = self.fig.add_subplot(
            1, 3, 3, projection=self.projection_crs,
        )

    def create_north_arrow(self, ax, x=None, y=None):
        width = self.width * 0.01
        height = self.height * 0.05
        head_width = width * 2.5
        head_length = height * 0.3
        if x is None:
            x = self.width * 0.82 + self.bbox[1]
        if y is None:
            y = self.height * 0.10 + self.bbox[0]
        ax.add_patch(mpatches.FancyArrow(
            x, y, 0, height, width=width,
            head_width=head_width, head_length=head_length,
            length_includes_head=True, color='black',
        ))
        ax.text(
            x, y - head_width * 0.20, 'N', c='#000000',
            fontsize=self.fs + 4, stretch='condensed', weight='bold',
            ha='center', va='top',
        )

    def set_map(self, ax, df=0):
        ax.set_extent([
            self.bbox[1] - df, self.bbox[3] + df,
            self.bbox[0] - df, self.bbox[2] + df,
        ], crs=self.projection_crs)
        grid_step = np.min([int(self.width / 5), int(self.height / 5)])
        gl = ax.gridlines(
            draw_labels=True, linewidth=0.5, linestyle='--', alpha=0.7, dms=True,
            xlocs=np.arange(
                int(self.bbox[1] - df), int(self.bbox[3] + df), grid_step,
            ),
            ylocs=np.arange(
                int(self.bbox[0] - df), int(self.bbox[2] + df), grid_step,
            ),
        )
        gl.xlabel_style = {'size': self.fs}
        gl.ylabel_style = {'size': self.fs}
        ax.add_image(cartopy.io.img_tiles.GoogleTiles(style='satellite'), 5)

    def draw_limits(
            self, ax, countries_shp_path=None,
            provinces_shp_path=None, departments_shp_path=None,
        ):
        if countries_shp_path is not None:
            countries = list(
                shpreader.Reader(countries_shp_path).geometries(),
            )
            ax.add_geometries(
                countries, self.projection_crs, edgecolor='black',
                facecolor='none', linewidth=0.5, linestyle='-',
            )
        if provinces_shp_path is not None:
            provinces = list(
                shpreader.Reader(provinces_shp_path).geometries(),
            )
            ax.add_geometries(
                provinces, self.projection_crs, edgecolor='black',
                facecolor='none', linewidth=0.2, linestyle=(10, (10, 10)),
            )
        if departments_shp_path is not None:
            departments = list(
                shpreader.Reader(departments_shp_path).geometries(),
            )
            ax.add_geometries(
                departments, self.projection_crs, edgecolor='black',
                facecolor='none', linewidth=0.2, linestyle='-.',
            )

    def draw_plot1(self, ax):
        ax.plot(
            self.station.time, self.station.data, c='black',
            lw=0.5, marker='o', markersize=2,
        )
        ax.set(ylabel='Daily Rain (mm)')
        ax.grid(alpha=0.4)

    def draw_plot2(self, ax, t, outliers):
        # ficha.ax_plot2.plot(station.result['Y_rx1day']['time'], station.result['Y_rx1day']['data'], c='black', lw=1.5, marker='o', markersize=2, label='Yearly')
        ax.plot(
            t, outliers['data_without_outliers'][-1], c='black',
            lw=1.5, marker='o', markersize=2, label='Yearly',
        )
        ax.plot(
            self.station.result['son_rx1day']['time'],
            self.station.result['son_rx1day']['data'],
            c='red', lw=0.5, marker='o', markersize=2, label='SON',
        )
        ax.plot(
            self.station.result['djf_rx1day']['time'],
            self.station.result['djf_rx1day']['data'],
            c='green', lw=0.5, marker='o', markersize=2, label='DJF',
        )
        ax.plot(
            self.station.result['mam_rx1day']['time'],
            self.station.result['mam_rx1day']['data'],
            c='blue', lw=0.5, marker='o', markersize=2, label='MAM',
        )
        ax.plot(
            self.station.result['jja_rx1day']['time'],
            self.station.result['jja_rx1day']['data'],
            c='orange', lw=0.5, marker='o', markersize=2, label='JJA',
        )
        ax.scatter(
            np.concatenate([np.concatenate([
                t[~np.isnan(outliers['high_outliers'][i])],
                t[~np.isnan(outliers['low_outliers'][i])],
            ]) for i in range(outliers['high_outliers'].shape[0])]),
            np.concatenate([np.concatenate([
                outliers['high_outliers'][
                    i, ~np.isnan(outliers['high_outliers'][i])
                ],
                outliers['low_outliers'][
                    i, ~np.isnan(outliers['low_outliers'][i])
                ],
            ]) for i in range(outliers['high_outliers'].shape[0])]),
            c='black', marker='x', s=50, label='Outlier',
        )
        ax.set(ylabel='rmax (mm)')
        ax.grid(alpha=0.4)
        ax.legend(loc=(1.02, 0.25))

    def draw_map1(self, ax):
        self.set_map(ax)
        self.draw_limits(
            ax,
            provinces_shp_path=Path(
                Path(os.getcwd()).parent, 'EarthData',
                'natural_earth_data', '10m_cultural',
                'ne_10m_admin_1_states_provinces.shp',
            ),
            countries_shp_path=Path(
                Path(os.getcwd()).parent, 'EarthData',
                'natural_earth_data', '10m_cultural',
                'ne_10m_admin_0_countries.shp',
            ),
        )
        self.create_north_arrow(ax)
        ax.scatter(
            self.station.lon, self.station.lat, s=50,
            facecolor='white', edgecolor='red', lw=1,
        )
        ax.scatter(self.station.lon, self.station.lat, s=2, c='red')
        ax.set_title('Location', fontsize=self.fs)

    def draw_table1(self, ax, tests, outliers):
        score = self.evaluate(tests)
        ax.set_axis_off()
        self.table = ax.table(
            cellText=np.array([
                [
                    'id', 'name', 'lon', 'lat', 'elevation',
                    'province/state', 'country', 'institution',
                    'record_time', 'start_month', 'file_name',
                    'Tests', 'Outliers',
                ],
                [
                    self.station.id         , self.station.name       ,
                    self.station.lon        , self.station.lat        ,
                    self.station.elevation  , self.station.province   ,
                    self.station.country    , self.station.institution,
                    self.station.record_time, self.station.start_month,
                    self.station.file       , self.tests_summary(tests),
                    ', '.join([
                        str(_) for _ in np.concatenate([
                            outliers['high_outliers'][
                                ~np.isnan(outliers['high_outliers'])
                            ],
                            outliers['low_outliers'][
                                ~np.isnan(outliers['low_outliers'])
                            ],
                        ])
                    ]),
                ],
            ]).T,
            cellLoc='center', loc='center',
        )
        self.table.auto_set_font_size(False)
        for cell in self.table.get_celld():
            self.table.get_celld()[cell].set_height(0.05)
            if cell[1] == 0:
                if cell[0] < 11:
                    self.table.get_celld()[cell].set(
                        facecolor='#6FB6DC', alpha=0.3,
                    )
                else:
                    self.table.get_celld()[cell].set(
                        facecolor='#6FDC88', alpha=0.3,
                    )
                self.table.get_celld()[cell].set_text_props(
                    ha='left', va='center', style='oblique',
                )
        self.table.get_celld()[(11, 0)].set_height(0.10)
        self.table.get_celld()[(11, 1)].set_height(0.10)
        self.table.auto_set_column_width(0)
        self.table.auto_set_column_width(1)

    @staticmethod
    def evaluate(tests_result):
        score = {'independence' : 0, 'trend' : 0, 'homogeneity' : 0}
        if 'iWW' in tests_result.keys():
            if int(tests_result['iWW']['index']) == 2:
                score['independence'] += 1
            elif int(tests_result['iWW']['index']) == 1:
                score['independence'] += 2
        if 'tMK' in tests_result.keys():
            if int(tests_result['tMK']['index'][0]) != 2:
                score['trend'] += 1
            elif int(tests_result['tMK']['index'][1]) != 2:
                score['trend'] += 2
        if 'hWI' in tests_result.keys():
            if int(tests_result['hWI']['index']) == 2:
                score['homogeneity'] += 1
            elif int(tests_result['hWI']['index']) == 1:
                score['homogeneity'] += 3
        if 'hMW' in tests_result.keys():
            if int(tests_result['hMW']['index']) == 2:
                score['homogeneity'] += 1
            elif int(tests_result['hMW']['index']) == 1:
                score['homogeneity'] += 3
        if 'hPE' in tests_result.keys():
            if int(tests_result['hPE']['index']) == 2:
                score['homogeneity'] += 1
            elif int(tests_result['hPE']['index']) == 1:
                score['homogeneity'] += 3
        return score
    
    @staticmethod
    def tests_summary(tests_result):
        iWW = tests_result['iWW']['result']
        hPE = tests_result['hPE']['result']
        cp = tests_result['hPE']['change_point']
        if 'tMK' in tests_result.keys():
            if int(tests_result['tMK']['index'][0]) != 2:
                if int(tests_result['tMK']['index'][1]) == 2:
                    if int(tests_result['tMK']['index'][0]) == 1:
                        tMK = 'pass 99% dec'
                    else:
                        tMK = 'pass 99% inc'
                else:
                    if int(tests_result['tMK']['index'][1]) == 1:
                        tMK = 'not pass dec'
                    elif int(tests_result['tMK']['index'][1]) == 3:
                        tMK = 'not pass inc'
            else:
                tMK = 'pass 95%'
        return f'i: {iWW}\nt: {tMK}\nh: {hPE} ({cp})'
    
class Card_IMERG(Card):
    """
    
    """

    def __init__(self, bbox, fontsize, station, save_path):
        super().__init__(bbox, fontsize, station, save_path)

    def create_figure(self, title=None, figsize=None, dpi=300):
        if figsize is None:
            scale_factor = 10 / np.max([self.width, self.height])
            figsize = (
                3 * self.width * scale_factor,
                self.height * scale_factor,
            )
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        if title is not None:
            self.fig.suptitle(title, fontsize=self.fs+2)
        self.ax_info1 = plt.subplot2grid(
            (3, 3), (0, 0), rowspan=3, fig=self.fig,
        )
        self.ax_plot1 = plt.subplot2grid((3, 3), (0, 1), fig=self.fig)
        self.ax_plot2 = plt.subplot2grid((3, 3), (1, 1), fig=self.fig)
        self.ax_map = plt.subplot2grid(
            (3, 3), (0, 2), rowspan=2, fig=self.fig,
            projection=self.projection_crs,
        )
        self.ax_plot3 = plt.subplot2grid((3, 3), (2, 1), fig=self.fig)
        self.ax_plot4 = plt.subplot2grid((3, 3), (2, 2), fig=self.fig)
        self.ax_plot1.sharex(self.ax_plot2)
        self.ax_plot2.sharex(self.ax_plot3)
    
    def add_imerg(self, imerg_e, imerg_l, imerg_f):
        self.imerg_e = imerg_e
        self.imerg_l = imerg_l
        self.imerg_f = imerg_f

    def draw_plot3(self, ax):
        t0 = self.station.result['Y_3_sorted_rx1day']['time']
        outliers0 = self.station.result['Y_rx1day']['outliers']
        t1 = self.imerg_e.result['Y_3_sorted_rx1day']['time']
        outliers1 = self.imerg_e.result['Y_rx1day']['outliers']
        t2 = self.imerg_l.result['Y_3_sorted_rx1day']['time']
        outliers2 = self.imerg_l.result['Y_rx1day']['outliers']
        t3 = self.imerg_f.result['Y_3_sorted_rx1day']['time']
        outliers3 = self.imerg_f.result['Y_rx1day']['outliers']
        ax.plot(
            t0, outliers0['data_without_outliers'][-1], c='black',
            lw=1.5, marker='o', markersize=2, label='Station',
        )
        ax.plot(
            t1, outliers1['data_without_outliers'][-1], c='red',
            lw=1.0, marker='o', markersize=2, label='IMERG-E',
        )
        ax.plot(
            t2, outliers2['data_without_outliers'][-1], c='blue',
            lw=1.0, marker='o', markersize=2, label='IMERG-L',
        )
        ax.plot(
            t3, outliers3['data_without_outliers'][-1], c='green',
            lw=1.0, marker='o', markersize=2, label='IMERG-F',
        )
        ax.scatter(
            np.concatenate([np.concatenate([
                t0[~np.isnan(outliers0['high_outliers'][i])],
                t0[~np.isnan(outliers0['low_outliers'][i])],
            ]) for i in range(outliers0['high_outliers'].shape[0])]),
            np.concatenate([np.concatenate([
                outliers0['high_outliers'][
                    i, ~np.isnan(outliers0['high_outliers'][i]),
                ],
                outliers0['low_outliers'][
                    i, ~np.isnan(outliers0['low_outliers'][i]),
                ],
            ]) for i in range(outliers0['high_outliers'].shape[0])]),
            c='black', marker='x', s=50, label='Outlier',
        )
        ax.scatter(
            np.concatenate([np.concatenate([
                t1[~np.isnan(outliers1['high_outliers'][i])],
                t1[~np.isnan(outliers1['low_outliers'][i])],
            ]) for i in range(outliers1['high_outliers'].shape[0])]),
            np.concatenate([np.concatenate([
                outliers1['high_outliers'][
                    i, ~np.isnan(outliers1['high_outliers'][i]),
                ],
                outliers1['low_outliers'][
                    i, ~np.isnan(outliers1['low_outliers'][i]),
                ],
            ]) for i in range(outliers1['high_outliers'].shape[0])]),
            c='red', marker='x', s=50,
        )
        ax.scatter(
            np.concatenate([np.concatenate([
                t2[~np.isnan(outliers2['high_outliers'][i])],
                t2[~np.isnan(outliers2['low_outliers'][i])],
            ]) for i in range(outliers2['high_outliers'].shape[0])]),
            np.concatenate([np.concatenate([
                outliers2['high_outliers'][
                    i, ~np.isnan(outliers2['high_outliers'][i]),
                ],
                outliers2['low_outliers'][
                    i, ~np.isnan(outliers2['low_outliers'][i]),
                ],
            ]) for i in range(outliers2['high_outliers'].shape[0])]),
            c='blue', marker='x', s=50,
        )
        ax.scatter(
            np.concatenate([np.concatenate([
                t3[~np.isnan(outliers3['high_outliers'][i])],
                t3[~np.isnan(outliers3['low_outliers'][i])],
            ]) for i in range(outliers3['high_outliers'].shape[0])]),
            np.concatenate([np.concatenate([
                outliers3['high_outliers'][
                    i, ~np.isnan(outliers3['high_outliers'][i])
                ],
                outliers3['low_outliers'][
                    i, ~np.isnan(outliers3['low_outliers'][i])
                ],
            ]) for i in range(outliers3['high_outliers'].shape[0])]),
            c='green', marker='x', s=50,
        )
        
        ax.set(ylabel='rmax yearly (mm)')
        ax.grid(alpha=0.4)
        ax.legend(loc=(1.02, 0.25))
        
    def draw_plot4(self, ax, T):
        lw, lw_, lw_i, lw_i_ = 1.5, 1.2, 1.2, 0.4
        ls, ls_, ls_i, ls_i_ = '-', '--', '-', '-.'

        ax.scatter(
            self.station.result['Y_rx1day']['lognorm'].return_period,
            self.station.result['Y_rx1day']['lognorm'].sorted_data,
            marker='x', c='black', s=5,
        )

        ax.plot(
            T, self.station.result['Y_rx1day']['lognorm'].ppf(T)[0],
            c='black', lw=lw_, ls=ls_,
        )
        ax.plot(
            T, self.station.result['Y_rx1day']['lognorm'].ppf(T)[1],
            c='black', lw=lw, ls=ls, label='Station',
        )
        ax.plot(
            T, self.station.result['Y_rx1day']['lognorm'].ppf(T)[2],
            c='black', lw=lw_, ls=ls_,
        )
        ax.plot(
            T, self.imerg_e.result['Y_rx1day']['lognorm'].ppf(T)[0],
            c='red', lw=lw_i_, ls=ls_i_,
        )
        ax.plot(
            T, self.imerg_e.result['Y_rx1day']['lognorm'].ppf(T)[1],
            c='red', lw=lw_i, ls=ls_i, label='IMERG-E',
        )
        ax.plot(
            T, self.imerg_e.result['Y_rx1day']['lognorm'].ppf(T)[2],
            c='red', lw=lw_i_, ls=ls_i_,
        )
        ax.plot(
            T, self.imerg_l.result['Y_rx1day']['lognorm'].ppf(T)[0],
            c='blue', lw=lw_i_, ls=ls_i_,
        )
        ax.plot(
            T, self.imerg_l.result['Y_rx1day']['lognorm'].ppf(T)[1],
            c='blue', lw=lw_i, ls=ls_i, label='IMERG-L',
        )
        ax.plot(
            T, self.imerg_l.result['Y_rx1day']['lognorm'].ppf(T)[2],
            c='blue', lw=lw_i_, ls=ls_i_,
        )
        ax.plot(
            T, self.imerg_f.result['Y_rx1day']['lognorm'].ppf(T)[0],
            c='green', lw=lw_i_, ls=ls_i_,
        )
        ax.plot(
            T, self.imerg_f.result['Y_rx1day']['lognorm'].ppf(T)[1],
            c='green', lw=lw_i, ls=ls_i, label='IMERG-F',
        )
        ax.plot(
            T, self.imerg_f.result['Y_rx1day']['lognorm'].ppf(T)[2],
            c='green', lw=lw_i_, ls=ls_i_,
        )

        ax.grid(alpha=0.4)

        ax.set_xlabel('Return Period (Years)', fontsize=self.fs)
        ax.set_ylabel('Rx1day (mm)', fontsize=self.fs)
    
    @staticmethod
    def add_row(table, row, text):
        table.add_cell(
            row, 0, table.get_celld()[(0, 0)].get_width(),
            table.get_celld()[(0, 0)].get_height(), text=text[0],
            facecolor='#FFC29B',
        )
        table.add_cell(
            row, 1, table.get_celld()[(0, 1)].get_width(),
            table.get_celld()[(0, 1)].get_height(), text=text[1],
        )
    
    @staticmethod
    def error(obs, est):
        return [
            sklearn.metrics.mean_squared_error(obs, est, squared=False),
            sklearn.metrics.mean_absolute_percentage_error(obs, est),
            nash_coeficient(obs, est)[1],
        ]

    def add_to_table1(self, T):
        score1 = self.tests_summary(
            self.imerg_e.result['Y_rx1day']['data_outliers_tests'],
        )
        score2 = self.tests_summary(
            self.imerg_l.result['Y_rx1day']['data_outliers_tests'],
        )
        score3 = self.tests_summary(
            self.imerg_f.result['Y_rx1day']['data_outliers_tests'],
        )
        error1 = self.error(
            self.station.result['Y_rx1day']['lognorm'].ppf(T)[1],
            self.imerg_e.result['Y_rx1day']['lognorm'].ppf(T)[1],
        )
        error2 = self.error(
            self.station.result['Y_rx1day']['lognorm'].ppf(T)[1],
            self.imerg_l.result['Y_rx1day']['lognorm'].ppf(T)[1],
        )
        error3 = self.error(
            self.station.result['Y_rx1day']['lognorm'].ppf(T)[1],
            self.imerg_f.result['Y_rx1day']['lognorm'].ppf(T)[1],
        )
        cells = np.array([_ for _ in self.table.get_celld()])
        last_row = np.max(cells[:, 0])
        self.add_row(self.table, last_row+1, ['Tests-E', score1])
        self.add_row(self.table, last_row+2, ['Tests-L', score2])
        self.add_row(self.table, last_row+3, ['Tests-F', score3])
        self.add_row(
            self.table, last_row+4, ['GoodFit(RMSE, MAPE, NNSE) - E',
            f'({np.round(error1[0], 1)} mm, {int(np.round(error1[1] * 100, 0))} %, {np.round(error1[2], 2)})']
        )
        self.add_row(
            self.table, last_row+5, ['GoodFit(RMSE, MAPE, NNSE) - L',
            f'({np.round(error2[0], 1)} mm, {int(np.round(error2[1] * 100, 0))} %, {np.round(error2[2], 2)})']
        )
        self.add_row(
            self.table, last_row+6, ['GoodFit(RMSE, MAPE, NNSE) - F',
            f'({np.round(error3[0], 1)} mm, {int(np.round(error3[1] * 100, 0))} %, {np.round(error3[2], 2)})']
        )
        for cell in self.table.get_celld():
            if cell[1] == 0:
                self.table.get_celld()[cell].set(alpha=0.3)
                self.table.get_celld()[cell].set_text_props(
                    ha='left', va='center', style='oblique',
                )
            elif cell[1] == 1:
                self.table.get_celld()[cell].set_text_props(
                    ha='center', va='center',
                )
        self.table.get_celld()[(13, 0)].set_height(0.10)
        self.table.get_celld()[(14, 0)].set_height(0.10)
        self.table.get_celld()[(15, 0)].set_height(0.10)
        self.table.get_celld()[(13, 1)].set_height(0.10)
        self.table.get_celld()[(14, 1)].set_height(0.10)
        self.table.get_celld()[(15, 1)].set_height(0.10)
        self.table.auto_set_column_width(0)
        self.table.auto_set_column_width(1)

