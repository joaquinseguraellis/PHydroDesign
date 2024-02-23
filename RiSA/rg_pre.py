"""
This module is made to process rainfall data.
"""

# Libraries

from .libraries import *
from .hidro_tools import *
sys.path.insert(0, os.getcwd())

# Functions

"""
Servicio Meteorológico Nacional (SMN). Information from Centro de Información Mateorológica
"""
def csv_SMN(main_dir, save_dir):
    """
    This function opens data from SMN and writes it to the complete data directory.
    File 192034.txt is the one containing the information under the follow columns:
        ESTAC	FECHA	TMAX	TMIN	TMED	PRCP	NUM_OBS
    First, it opens the file provided by SMN and convert it to an array.
    Then, it takes precipitation data column and replace ' ' with 0 and 'S/D' with NaN.
    Then, it opens its metadata from estaciones.csv.
    Finally, it writes precipitation data completed by function "complete_data" to a csv with it's metadata.
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    with open(Path(main_dir, '192034.txt'), 'r') as file:
        data = [_.replace(',', '.').split('\t') for _ in file.readlines()]
    data = np.array(data[1:])[:, :-1]
    id_col = np.unique(data[:, 0])
    for id_ in id_col:
        if f'SMN_{id_}.csv' not in os.listdir(save_dir):
            time = np.array([datetime.datetime.strptime(_, '%d/%m/%Y') + datetime.timedelta(days=1) for _ in data[np.where(data[:, 0] == id_)[0], 1]])
            prec = data[np.where(data[:, 0] == id_)[0], 5]
            prec[np.where(prec == ' ')] = 0
            prec[np.where(prec == 'S/D')] = np.nan
            time, prec = complete_data(time, prec)
            info_file_name = 'estaciones.csv'
            with open(Path(main_dir, info_file_name), 'r', newline='', encoding='utf-8') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                data_info = np.array([row for row in spamreader])
            data_info = data_info[np.where(data_info[:, 0] == id_)].flatten()
            with open(Path(save_dir, f'{data_info[22]}_{id_}.csv'), 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                spamwriter.writerow(['id', id_])
                spamwriter.writerow(['name', data_info[1]])
                spamwriter.writerow(['lon', data_info[10]])
                spamwriter.writerow(['lat', data_info[11]])
                spamwriter.writerow(['elevation', data_info[12]])
                spamwriter.writerow(['province/state', data_info[14]])
                spamwriter.writerow(['country', data_info[21]])
                spamwriter.writerow(['institution', data_info[22]])
                spamwriter.writerow(['record_time', '12:00:00 UTC'])
                spamwriter.writerow(['time', 'prec (mm)'])
                for i in range(time.shape[0]):
                    spamwriter.writerow([time[i].date(), prec[i]])

"""
Instituto Nacional de Tecnología Agropecuaria (INTA). Information downloaded from Sistema de Información y Gestión Agrometeorológica (SIGA).
URL: http://siga.inta.gob.ar/#/
"""
def get_INTA_prec(path):
    """
    This function opens INTA .xls files and returns time and precipitation data.
    """
    with xlrd.open_workbook(path) as wb:
        ws1 = wb.sheet_by_index(0)
        aux = np.array([_.value for _ in ws1.col(11)[1:]])
        time = np.array([datetime.datetime.strptime(_.value[:10], '%Y-%m-%d') + datetime.timedelta(days=1) for _ in ws1.col(0)[1:]])[np.where(aux != '')]
        prec = np.array([_.value for _ in ws1.col(11)[1:]])[np.where(aux != '')].astype('f')
    return time, prec

def csv_INTA(main_dir, save_dir):
    """
    This function opens data from INTA and writes it to the complete data directory.
    First, it opens .xls files with "get_INTA_prec" function and it's metadata from estaciones.csv.
    Then, it writes precipitation data completed by function "complete_data" to a csv with its metadata.
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for file in os.listdir(Path(main_dir, 'INTA_xls')):
        id_ = file[:file.index('.')]
        if f'INTA_{id_}.csv' not in os.listdir(save_dir):
            time, prec = get_INTA_prec(Path(main_dir, 'INTA_xls', f'{id_}.xls'))
            time, prec = complete_data(time, prec)
            info_file_name = 'estaciones.csv'
            with open(Path(main_dir, info_file_name), 'r', newline='', encoding='utf-8') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                data_info = np.array([row for row in spamreader])
            data_info = data_info[np.where(data_info[:, 0] == id_)].flatten()
            with open(Path(save_dir, f'{data_info[22]}_{id_}.csv'), 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                spamwriter.writerow(['id', id_])
                spamwriter.writerow(['name', data_info[1]])
                spamwriter.writerow(['lon', data_info[10]])
                spamwriter.writerow(['lat', data_info[11]])
                spamwriter.writerow(['elevation', data_info[12]])
                spamwriter.writerow(['province/state', data_info[14]])
                spamwriter.writerow(['country', data_info[21]])
                spamwriter.writerow(['institution', data_info[22]])
                spamwriter.writerow(['record_time', '03:00:00 UTC'])
                spamwriter.writerow(['time', 'prec (mm)'])
                for i in range(time.shape[0]):
                    spamwriter.writerow([time[i].date(), prec[i]])

"""
Sistema Nacional de Información Hídrica (SNIH). Information downloaded from its URL.
URL: https://snih.hidricosargentina.gob.ar/Inicio.aspx
"""
def get_SNIH_prec(path):
    """
    This function opens SNIH .xlsx files and returns time and precipitation data.
    """
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    info = ws.cell(1, 1).value
    time = list()
    for _ in list(ws.iter_cols(max_col=1, values_only=True))[0][2:]:
        try:
            time.append(datetime.datetime.strptime(str(_), '%d/%m/%Y %H:%M').replace(hour=0, minute=0))
        except:
            try:
                time.append(datetime.datetime.strptime(str(_), '%Y-%m-%d %H:%M:%S').replace(hour=0, minute=0))
            except:
                time.append(datetime.datetime.strptime(str(_), '%d-%m-%Y %H:%M').replace(hour=0, minute=0))
    time = np.array(time)
    prec = list()
    for _ in list(ws.iter_cols(min_col=2, max_col=2, values_only=True))[0][2:]:
        if 'Acum' in str(_):
            _ = str(_)[:str(_).index(' ')]
        if '' == str(_):
            prec.append(np.nan)
        else:
            prec.append(float(_))
    prec = np.array(prec)
    return time, prec

def csv_SNIH(main_dir, save_dir):
    """
    This function opens data from SNIH and writes it to the complete data directory.
    First, it opens .xls files with "get_SNIH_prec" function and it's metadata from estaciones.csv.
    Then, it writes precipitation data completed by function "complete_data" to a csv with its metadata.
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for file in os.listdir(Path(main_dir, 'SNIH_xlsx')):
        id_ = file[:file.index('.')]
        id_ = id_[id_.index(' ') + 1:]
        if f'SNIH_{id_}.csv' not in os.listdir(save_dir):
            time, prec = get_SNIH_prec(Path(main_dir, 'SNIH_xlsx', file))
            time, prec = complete_data(time, prec)
            info_file_name = 'info_SNIH.csv'
            with open(Path(main_dir, info_file_name), 'r', newline='', encoding='utf-8') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                data_info = np.array([row for row in spamreader])
            data_info = data_info[np.where(data_info[:, 0] == id_)].flatten()
            if data_info.shape[0] == 0:
                data_info = np.zeros(30)
                data_info[:] = np.nan
                lon = np.nan
                lat = np.nan
            else:
                lon = data_info[16]
                lon = - float(lon[:lon.index('º')]) - float(lon[lon.index('º')+2:lon.index('\'')]) / 60 - float(lon[lon.index('\'')+2:lon.index('\"')]) / 3600
                lat = data_info[15]
                lat = - float(lat[:lat.index('º')]) - float(lat[lat.index('º')+2:lat.index('\'')]) / 60 - float(lat[lat.index('\'')+2:lat.index('\"')]) / 3600
            with open(Path(save_dir, f'SNIH_{id_}.csv'), 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                spamwriter.writerow(['id', id_])
                spamwriter.writerow(['name', data_info[1]])
                spamwriter.writerow(['lon', lon])
                spamwriter.writerow(['lat', lat])
                spamwriter.writerow(['elevation', data_info[12]])
                spamwriter.writerow(['province/state', data_info[8]])
                spamwriter.writerow(['country', 'AR'])
                spamwriter.writerow(['institution', 'SNIH'])
                spamwriter.writerow(['record_time', '12:00:00 UTC'])
                spamwriter.writerow(['time', 'prec (mm)'])
                for i in range(time.shape[0]):
                    spamwriter.writerow([time[i].date(), prec[i]])

"""
Instituto Nacional del Agua - Subgerencia del Centro de la Región Semiárida (INA-CIRSA). Information downloaded from Sistema de Gestión de Amenazas (SGA).
URL: https://sgainacirsa.ddns.net/cirsa/login.xhtml
"""
def get_INA_prec(path):
    """
    This function opens INTA .xls files and returns time and precipitation data.
    """
    with xlrd.open_workbook(path) as wb:
        ws1 = wb.sheet_by_index(0)
        time = np.array([datetime.datetime.strptime(_.value, '%d/%m/%Y %H:%M') for _ in ws1.col(1)[1:]])
        prec = np.array([_.value for _ in ws1.col(3)][1:]).astype('f')
    return time, prec

def daily_prec(time, prec):
    """
    This function calculate daily acumulated data from 9 to 9 GTM-3 (12 to 12 UTC).
    """
    first_day = datetime.datetime(time[0].year, time[0].month, time[0].day, 9, 0)
    last_day = datetime.datetime(time[-1].year, time[-1].month, time[-1].day, 9, 0)
    time_ = np.arange(
        first_day,
        last_day + datetime.timedelta(days=2),
        datetime.timedelta(days=1),
    ).astype(datetime.datetime)
    prec_ = np.zeros((time_.shape[0]))
    for i, t in tqdm(enumerate(time)):
        if t < datetime.datetime(t.year, t.month, t.day, 9, 0):
            prec_[list(time_).index(datetime.datetime(t.year, t.month, t.day, 9, 0))] += prec[i]
        else:
            prec_[list(time_).index(datetime.datetime(t.year, t.month, t.day, 9, 0)) + 1] += prec[i]
    return np.array([_.replace(hour=0) for _ in time_]), prec_

def csv_INA(main_dir, save_dir):
    """
    This function opens data from INTA and writes it to the complete data directory.
    First, it opens .xls files with "get_INTA_prec" function and get the daily acumulated data with the "daily_prec" function.
    Then, it opens its metadata from estaciones.csv.
    Finally, it writes precipitation data completed by function "complete_data" to a csv with its metadata.
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for file in os.listdir(Path(main_dir, 'INA_xls')):
        id_ = file[:file.index('.')]
        if f'INA_{id_}.csv' not in os.listdir(save_dir):
            time, prec = get_INA_prec(Path(main_dir, 'INA_xls', file))
            time, prec = daily_prec(time, prec)
            time, prec = complete_data(time, prec)
            info_file_name = 'estaciones.csv'
            with open(Path(main_dir, info_file_name), 'r', newline='', encoding='utf-8') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                data_info = np.array([row for row in spamreader])
            data_info = data_info[np.where(data_info[:, 0] == id_)].flatten()
            with open(Path(save_dir, f'{data_info[22]}_{id_}.csv'), 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                spamwriter.writerow(['id', id_])
                spamwriter.writerow(['name', data_info[1]])
                spamwriter.writerow(['lon', data_info[10]])
                spamwriter.writerow(['lat', data_info[11]])
                spamwriter.writerow(['elevation', data_info[12]])
                spamwriter.writerow(['province/state', data_info[14]])
                spamwriter.writerow(['country', data_info[21]])
                spamwriter.writerow(['institution', data_info[22]])
                spamwriter.writerow(['record_time', '12:00:00 UTC'])
                spamwriter.writerow(['time', 'prec (mm)'])
                for i in range(time.shape[0]):
                    spamwriter.writerow([time[i].date(), prec[i]])

def preprocess_data(load_dir, save_dir, delete_year_path):
    """
    This function runs the preprocess method from Rain_Gauge class.
    First, it reads a list of years to delete, selected manually.
    Then, it get the hydrological year for the data and delete incomplete years and provided.
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for file in os.listdir(load_dir):
        if file not in os.listdir(save_dir):
            with open(delete_year_path, 'r', newline='') as csvfile:
                data = np.array(list(csv.reader(csvfile, delimiter=',')))
            delete_years = data[data[:, 0] == file, 1:][0]
            delete_years = delete_years[delete_years != ''].astype('int')
            name = file[:file.find('.')]
            station_preprocess = Rain_Gauge(Path(load_dir, file))
            station_preprocess.preprocess(delete_years)
            station_preprocess.save(Path(save_dir, file))

def trim_data(load_dir, first_year, last_year):
    """
    This function trims data to the period of IMERG data.
    It reads what is the start_month of data hydrological year, to adecuate trim dates.
    Finally, ir writes data to a new folder if there is enough information for frequency analysis. It is selected those with 14 or more years.
    """
    result_dir = Path(load_dir.parent, f'{load_dir.name}_{first_year}_{last_year}')
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    for file in os.listdir(load_dir): 
        if file not in os.listdir(result_dir):
            name = file[:file.find('.')]
            station_preprocess = Rain_Gauge()
            station_preprocess.load(Path(load_dir, file))
            if station_preprocess.start_month >= 7:
                first_year_ = first_year
            else:
                first_year_ = first_year + 1
            station_preprocess.data = station_preprocess.data[station_preprocess.time >= datetime.datetime(first_year_, station_preprocess.start_month, 1)]
            station_preprocess.time = station_preprocess.time[station_preprocess.time >= datetime.datetime(first_year_, station_preprocess.start_month, 1)]
            station_preprocess.data = station_preprocess.data[station_preprocess.time < datetime.datetime(last_year, station_preprocess.start_month, 1)]
            station_preprocess.time = station_preprocess.time[station_preprocess.time < datetime.datetime(last_year, station_preprocess.start_month, 1)]
            n = station_preprocess.data[~np.isnan(station_preprocess.data)].shape[0]
            if 'Base' not in station_preprocess.name and n > 0:
                station_preprocess.save(Path(result_dir, file))

def run_preprocess(main_dir):
    csv_SMN(main_dir, Path(main_dir, 'complete_csv'))
    csv_INTA(main_dir, Path(main_dir, 'complete_csv'))
    csv_SNIH(main_dir, Path(main_dir, 'complete_csv'))
    csv_INA(main_dir, Path(main_dir, 'complete_csv'))
    preprocess_data(Path(main_dir, 'complete_csv'), Path(main_dir, 'preprocess_csv'), Path(main_dir, 'delete_years.csv'))