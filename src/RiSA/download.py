"""
This module is used for frequency analysis of hydrological data.
"""

# Libraries

import os, platform, shutil, datetime, time
import requests

import numpy as np
import pandas as pd
import multiprocessing as mp

from pathlib import Path
from subprocess import Popen

# from .libraries import *

# Functions

def download_credentials(urs, username, password):
    """
    Credentials for downloading from Earth Data
    """
    homeDir = os.path.expanduser("~") + os.sep
    with open(homeDir + '.netrc', 'w') as file:
        file.write(f'machine {urs} login {username} password {password}')
        file.close()
    with open(homeDir + '.urs_cookies', 'w') as file:
        file.write('')
        file.close()
    with open(homeDir + '.dodsrc', 'w') as file:
        file.write('HTTP.COOKIEJAR={}.urs_cookies\n'.format(homeDir))
        file.write('HTTP.NETRC={}.netrc'.format(homeDir))
        file.close()
    print('Saved .netrc, .urs_cookies, and .dodsrc to:', homeDir)
    # Set appropriate permissions for Linux/macOS
    if platform.system() != "Windows":
        Popen('chmod og-rw ~/.netrc', shell=True)
    else:
        # Copy dodsrc to working directory in Windows  
        shutil.copy2(homeDir + '.dodsrc', os.getcwd())
        print('Copied .dodsrc to:', os.getcwd())

# Classes

class Download_IMERG:
    """Download IMERG data from "start_date" to "end_date" for the rectangle of longitud "lon1" to "lon2" and latitude "lat1" to "lat2".
    It saves the files in a new folder of name "title" located in "save_path".
    It is required to specify the version of IMERG needed (Early, Late and Final) and the frequency of data (1D for daily and 30T for half hourly).
    """

    def __init__(self, freq, version, bbox=None, save_path=os.getcwd()):
        if freq != '30T' and freq != '1D':
            raise ValueError('Time frequency must be 1D for daily and 30T for half-hourly.')
        if version != 'Early' and version != 'Late' and version != 'Final':
            raise ValueError('Version is not valid, choose Early, Late or Final.')
        self.freq = freq
        self.version = version
        lons = [i/100 for i in range(-17995, 17996, 10)]
        lats = [i/100 for i in range(-8995, 8996, 10)]
        if not bbox is None:
            self.bbox = [lons.index(bbox[0]), lons.index(bbox[1]), lats.index(bbox[2]), lats.index(bbox[3])]
        else:
            self.bbox = [0, len(lons) - 1, 0, len(lats) - 1]
        self.save_path = save_path

    def generate_url(self, dt, freq, version):
        if freq == '1D':
            if version == 'Final' or version == 'final':
                return f'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDF.06/{dt.year}/{dt.month:02}/3B-DAY.MS.MRG.3IMERG.{dt.year}{dt.month:02}{dt.day:02}-S000000-E235959.V06.nc4'
            if version == 'Late' or version == 'late':
                return f'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDL.06/{dt.year}/{dt.month:02}/3B-DAY-L.MS.MRG.3IMERG.{dt.year}{dt.month:02}{dt.day:02}-S000000-E235959.V06.nc4'
            if version == 'Early' or version == 'early':
                return f'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDE.06/{dt.year}/{dt.month:02}/3B-DAY-E.MS.MRG.3IMERG.{dt.year}{dt.month:02}{dt.day:02}-S000000-E235959.V06.nc4'
        elif freq == '30T':
            dt = dt - datetime.timedelta(minutes=30)
            minutes = dt.hour * 60 + dt.minute
            day_of_year = dt.strftime('%j')
            if version == 'Final' or version == 'final':
                return f'https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.06/{dt.year}/{day_of_year}/3B-HHR.MS.MRG.3IMERG.{dt.year}{dt.month:02}{dt.day:02}-S{dt.hour:02}{dt.minute:02}00-E{dt.hour:02}{dt.minute+29:02}59.{minutes:04}.V06B.HDF5.nc4?precipitationCal[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],precipitationUncal[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],HQprecipitation[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],IRprecipitation[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],time,lon[{self.bbox[0]}:{self.bbox[1]}],lat[{self.bbox[2]}:{self.bbox[3]}]'
            if version == 'Late' or version == 'late':
                return f'https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHHL.06/{dt.year}/{day_of_year}/3B-HHR-L.MS.MRG.3IMERG.{dt.year}{dt.month:02}{dt.day:02}-S{dt.hour:02}{dt.minute:02}00-E{dt.hour:02}{dt.minute+29:02}59.{minutes:04}.V06B.HDF5.nc4?precipitationCal[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],precipitationUncal[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],HQprecipitation[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],IRprecipitation[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],time,lon[{self.bbox[0]}:{self.bbox[1]}],lat[{self.bbox[2]}:{self.bbox[3]}]'
            if version == 'Early' or version == 'early':
                return f'https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHHE.06/{dt.year}/{day_of_year}/3B-HHR-E.MS.MRG.3IMERG.{dt.year}{dt.month:02}{dt.day:02}-S{dt.hour:02}{dt.minute:02}00-E{dt.hour:02}{dt.minute+29:02}59.{minutes:04}.V06B.HDF5.nc4?precipitationCal[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],precipitationUncal[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],HQprecipitation[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],IRprecipitation[0:0][{self.bbox[0]}:{self.bbox[1]}][{self.bbox[2]}:{self.bbox[3]}],time,lon[{self.bbox[0]}:{self.bbox[1]}],lat[{self.bbox[2]}:{self.bbox[3]}]'

    @staticmethod
    def download_url(args):
        url, fp = args[0], args[1]
        if not os.path.exists(fp):
            try_count = 0
            while try_count < 5:
                try:
                    result = requests.get(url, timeout=15)
                    with open(fp, 'wb') as f:
                        f.write(result.content)
                    try:
                        with open(fp,'rb') as f:
                            if f.readlines()[26] == 'Service Temporarily Unavailable':
                                print(f'{url} is temporarily unavailable')
                                time.sleep(2)
                                os.remove(fp)
                                try_count += 1
                                continue
                            else:
                                break
                    except:
                        pass
                except Exception as e:
                    try_count += 1
                    print(f'Error downloading from {url} and saving to {fp}. Error: {e}')
                    time.sleep(1)
    
    @staticmethod
    def all_exists(paths):
        return np.all([os.path.exists(_) for _ in paths])

    def download(
            self, start_datetime, end_datetime,
            multiprocess=True, cpu_count=2
    ):
        dts = pd.date_range(
            start=start_datetime, end=end_datetime, freq=self.freq,
        )
        urls = [
            self.generate_url(dt, self.freq, self.version)
            for dt in dts
        ]
        base = f'IMERG_{self.version}_{self.freq}_'
        file_paths = [
            Path(
                self.save_path,
                f'{base}{dt.year:04}{dt.month:02}{dt.day:02}{dt.hour:02}{dt.minute:02}.hdf5',
            )
            for dt in dts
        ]
        inputs = zip(urls, file_paths)
        if multiprocess:
            with mp.pool.ThreadPool(cpu_count) as executor:
                executor.imap_unordered(self.download_url, inputs)
                while not self.all_exists(file_paths):
                    pass
        else:
            for _ in inputs:
                self.download_url(_)