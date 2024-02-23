"""
This module is made to process rainfall data.
"""

# Libraries

from .libraries import *

# Functions

def complete_data(time, prec, delta=datetime.timedelta(days=1)):
    """
    This function takes precipitacion data array and the associated time array.
    First, it complete time array from 1st of January of the first year to 31th of December of the last year.
    Then, it complete with NaN values where data is missing.
    Returns completed time and precipitation arrays.
    """
    time_ = np.arange(
        datetime.datetime(time[0].year, 1, 1),
        datetime.datetime(time[-1].year, 12, 31) + datetime.timedelta(days=1),
        delta,
    ).astype(datetime.datetime)
    prec_ = np.zeros((time_.shape[0]))
    prec_[:] = np.nan
    aux = 0
    for i in range(time.shape[0]):
        aux = list(time_).index(time[i], aux)
        prec_[aux] = prec[i]
    return time_, prec_

def adjacent_months(month: int, steps: int = 1) -> tuple:
    """
    This functions return the previous and next "steps" months from "month".
    """
    if (not isinstance(month, int)) or (not isinstance(steps, int)):
        raise TypeError('TypeError: "month" and "steps" must be integers.')
    if steps > 6 or steps < 1:
        raise ValueError('ValueError: "steps" must be an integer from 1 to 6.')
    prev_ = month - steps
    next_ = month + steps
    if prev_ < 1:
        prev_ += 12
    if next_ > 12:
        next_ -= 12
    return prev_, next_

# Classes

class Rainfall_Indices:
    """
    Get climate indices information from rainfall data.

    Parameters:

    - time : numpy.ndarray, dtype=datetime64 or np.dtype('M')
        A 1 dimension ndarray with that must be completed from the
        first to the last element with the required frequency.
    
    - data : numpy.ndarray, dtype=float
        A 1, 2 or 3 dimension ndarray in which one dimension 
        corresponds with time's dimension.

    - axis : int
        It is 0 for default but can be change to 1 or 2 if time's
        dimension is not 0 in data array.

    - period : list of strings
        A list with all periods to analyze. Just yearly period (Y)
        for default but can take seasonal periods (jja, son, djf,
        mam) or monthly period (M). Output is going to be arange
        as this input.

    - start_month : int
        It can take values from 1 to 12 refering each month of the
        year and just works for yearly period. It is 7 (July) for 
        default.
    """
    def __init__(self, time, data, axis=0, period=['Y'], start_month=7):
        self.time = time
        if axis != 0:
            self.data = self.reshape_data(data, axis)
        else:
            self.data = data
        self.period = period
        self.start_month = start_month
        self.result = dict()

    def calculate(self):
        self.rxDday_calc(1)
        self.rQp_calc(95)
        self.rQmm_calc(95)
        self.rtot_calc()
        self.cwd_calc()
        self.cdd_calc()
        self.sorted_max_calc()
    
    @staticmethod
    def reshape_data(data, axis):
        """
        This method modify the data axis as specified.
        """
        axes = [i for i in range(len(data.shape))]
        axes.remove(axis)
        return np.transpose(data, axes=[axis] + axes)
    
    @staticmethod
    def trim_data_yearly(time, data, start_month=7):
        """
        This method trim the begining and end of the data to the hidrological year with start_month specified.
        """
        inicial_datetime = time[0]
        final_datetime = time[-1] + datetime.timedelta(days=1)
        dt_0 = datetime.datetime(inicial_datetime.year, start_month, 1)
        dt_0_ = datetime.datetime(inicial_datetime.year + 1, start_month, 1)
        if inicial_datetime != dt_0:
            if inicial_datetime < dt_0:
                data = data[np.where(time == dt_0)[0][0]:]
                time = time[np.where(time == dt_0)[0][0]:]
            else:
                data = data[np.where(time == dt_0_)[0][0]:]
                time = time[np.where(time == dt_0_)[0][0]:]
        dt_1 = datetime.datetime(final_datetime.year, start_month, 1)
        dt_1_ = datetime.datetime(final_datetime.year - 1, start_month, 1)
        if final_datetime != dt_1:
            if final_datetime < dt_1:
                data = data[:np.where(time == dt_1_)[0][0]]
                time = time[:np.where(time == dt_1_)[0][0]]
            else:
                data = data[:np.where(time == dt_1)[0][0]]
                time = time[:np.where(time == dt_1)[0][0]]
        return time, data
    
    @staticmethod
    def cut_data_yearly(time, data, start_month=7):
        """
        This method cut every year and return a list with them.
        """
        years = np.unique([time_.year for time_ in time])
        if start_month != 1:
            index_year = -2
            time_ = np.array([datetime.datetime(year, start_month, 1) for year in years[:-1]])
        else:
            index_year = -1
            time_ = np.array([datetime.datetime(year, start_month, 1) for year in years])
        data_ = [
            data[
                np.where(time == datetime.datetime(year, start_month, 1))[0][0]:np.where(time == datetime.datetime(year + 1, start_month, 1))[0][0]
            ] for year in years[:index_year]
        ]
        data_ = data_ + [data[np.where(time == datetime.datetime(years[index_year], start_month, 1))[0][0]:]]
        return time_, data_
    
    @staticmethod
    def trim_data_monthly(time, data, m=None):
        """
        This method trim the begining and end of the data to the hidrological year with start_month specified.
        Use this for monthly or seasonal analysis.
        """
        if m != None:
            inicial_datetime = time[0]
            if inicial_datetime != datetime.datetime(inicial_datetime.year, m[0], 1):
                if inicial_datetime < datetime.datetime(inicial_datetime.year, m[0], 1):
                    data = data[np.where(time == datetime.datetime(inicial_datetime.year, m[0], 1))[0][0]:]
                    time = time[np.where(time == datetime.datetime(inicial_datetime.year, m[0], 1))[0][0]:]
                else:
                    data = data[np.where(time == datetime.datetime(inicial_datetime.year + 1, m[0], 1))[0][0]:]
                    time = time[np.where(time == datetime.datetime(inicial_datetime.year + 1, m[0], 1))[0][0]:]
            final_datetime = time[-1] + datetime.timedelta(days=1)
            if final_datetime != datetime.datetime(final_datetime.year, m[-1], 1) + relativedelta(months=1):
                if final_datetime < datetime.datetime(final_datetime.year, m[-1], 1) + relativedelta(months=1):
                    data = data[:np.where(time == datetime.datetime(final_datetime.year - 1, m[-1], 1) + relativedelta(months=1))[0][0]]
                    time = time[:np.where(time == datetime.datetime(final_datetime.year - 1, m[-1], 1) + relativedelta(months=1))[0][0]]
                else:
                    data = data[:np.where(time == datetime.datetime(final_datetime.year, m[-1], 1) + relativedelta(months=1))[0][0]]
                    time = time[:np.where(time == datetime.datetime(final_datetime.year, m[-1], 1) + relativedelta(months=1))[0][0]]
            months = np.array([_.month for _ in time])
            data = np.concatenate([data[np.where(months == _)] for _ in m], axis=0)
            time = np.concatenate([time[np.where(months == _)] for _ in m], axis=0)
            time_sort = np.array(sorted(time))
            data = np.array([data[np.where(time == _)[0][0]] for _ in time_sort])
            time = time_sort
        else:
            inicial_datetime = time[0]
            if inicial_datetime != datetime.datetime(inicial_datetime.year, inicial_datetime.month, 1):
                data = data[np.where(time == datetime.datetime(inicial_datetime.year, inicial_datetime.month, 1) + relativedelta(months=1))[0][0]:]
                time = time[np.where(time == datetime.datetime(inicial_datetime.year, inicial_datetime.month, 1) + relativedelta(months=1))[0][0]:]
            final_datetime = time[-1] + datetime.timedelta(days=1)
            if final_datetime != datetime.datetime(final_datetime.year, final_datetime.month, 1):
                data = data[:np.where(time == datetime.datetime(final_datetime.year, final_datetime.month, 1))[0][0]]
                time = time[:np.where(time == datetime.datetime(final_datetime.year, final_datetime.month, 1))[0][0]]
        return time, data
    
    @staticmethod
    def cut_data_monthly(time, data, m=None):
        """
        This method cut every year and return a list with them.
        Use this for monthly or seasonal analysis.
        """
        if m != None:
            time_ = list()
            data_ = list()
            years = np.unique(np.array([_.year for _ in time]))
            for year in years[:-1]:
                time_.append(datetime.datetime(year, m[0], 1))
                data_.append(data[np.where(time == time_[-1])[0][0]:np.where(time == time_[-1] + relativedelta(months=len(m), days=-1))[0][0] + 1])
            if 12 not in m and 1 not in m:
                time_.append(datetime.datetime(years[-1], m[0], 1))
                data_.append(data[np.where(time == time_[-1])[0][0]:])
        else:
            time_ = list()
            data_ = list()
            years = np.array([_.year for _ in time])
            years_ = np.unique(years)
            months = np.array([_.month for _ in time])
            for year in years_:
                months_ = months[np.where(years == year)]
                year_data = data[np.where(years == year)]
                for month in np.unique(months_):
                    time_.append(datetime.datetime(year, month, 1))
                    data_.append(year_data[np.where(months_ == month)])
        return np.array(time_), data_
    
    def get_data(self, p, q=0.95):
        """
        This method trim and cut data as requested by periods.
        """
        if p == 'Y':
            time_, data_ = self.trim_data_yearly(self.time, self.data, self.start_month)
            q_95 = np.nanquantile(data_, q, axis=0)
            time_, data_ = self.cut_data_yearly(time_, data_, self.start_month)
        elif p == 'M':
            time_, data_ = self.trim_data_monthly(self.time, self.data)
            q_95 = np.nanquantile(data_, q, axis=0)
            time_, data_ = self.cut_data_monthly(time_, data_)
        elif p == 'jja':
            time_, data_ = self.trim_data_monthly(self.time, self.data, m=[6, 7, 8])
            q_95 = np.nanquantile(data_, q, axis=0)
            time_, data_ = self.cut_data_monthly(time_, data_, m=[6, 7, 8])
        elif p == 'son':
            time_, data_ = self.trim_data_monthly(self.time, self.data, m=[9, 10, 11])
            q_95 = np.nanquantile(data_, q, axis=0)
            time_, data_ = self.cut_data_monthly(time_, data_, m=[9, 10, 11])
        elif p == 'djf':
            time_, data_ = self.trim_data_monthly(self.time, self.data, m=[12, 1, 2])
            q_95 = np.nanquantile(data_, q, axis=0)
            time_, data_ = self.cut_data_monthly(time_, data_, m=[12, 1, 2])
        elif p == 'mam':
            time_, data_ = self.trim_data_monthly(self.time, self.data, m=[3, 4, 5])
            q_95 = np.nanquantile(data_, q, axis=0)
            time_, data_ = self.cut_data_monthly(time_, data_, m=[3, 4, 5])
        return time_, data_, q_95

    def get_sum(self, data, s):
        aux = np.ones([s - 1] + list(data.shape[1:]))
        aux[:] = np.nan
        try:
            return np.concatenate([aux, np.nansum(np.array([data[i:i+data.shape[0]-s+1] for i in range(s)]), axis=0)])
        except:
            print(aux)
            print((np.nansum(np.array([data[i:i+data.shape[0]-s+1] for i in range(s)]), axis=0)))

    def rxDday_calc(self, D):
        """
        This method returns annual maximum as requested by periods and for "D" days of accumulation.
        """
        for p in self.period:
            time, data, _ = self.get_data(p)
            rxDday = np.array([np.nanmax(self.get_sum(data_, D), axis=0) for data_ in data])
            rxDday[rxDday == 0] = np.nan
            self.result[f'{p}_rx{D}day'] = {'time' : time, 'data' : rxDday}
    
    def rQp_calc(self, Q):
        """
        This method returns annual sum of higher data than quantile "Q" as requested by periods.
        """
        for p in self.period:
            time, data, q = self.get_data(p, Q/100)
            data = [np.where(data_ >= 1, data_, 0) for data_ in data]
            rQp = np.array([np.nansum(np.where(data_ >= q, data_, 0), axis=0) for data_ in data])
            rQp[rQp == 0] = np.nan
            self.result[f'{p}_r{Q}p'] = {'time' : time, 'data' : rQp}
    
    def rQmm_calc(self, Q, L=None):
        """
        This method returns annual amount of higher data than quantile "Q" or value "L" as requested by periods.
        """
        for p in self.period:
            if L is not None:
                rQmm = np.array([np.nansum(np.where(np.where(data_ >= 1, data_, 0.) >= L, 1., 0.), axis=0) for data_ in data])
                rQmm[rQmm == 0.] = np.nan
                self.result[f'{p}_rL{Q}mm'] = {'time' : time, 'data' : rQmm}
            else:
                time, data, q = self.get_data(p, Q/100)
                rQmm = np.array([np.nansum(np.where(np.where(data_ >= 1, data_, 0.) >= q, 1., 0.), axis=0) for data_ in data])
                rQmm[rQmm == 0.] = np.nan
                self.result[f'{p}_rQ{Q}mm'] = {'time' : time, 'data' : rQmm}
    
    def rtot_calc(self):
        """
        This method returns annual sum as requested by periods.
        """
        for p in self.period:
            time, data, _ = self.get_data(p)
            rtot = np.array([np.nansum(np.where(data_ >= 1, data_, 0), axis=0) for data_ in data])
            rtot[rtot == 0] = np.nan
            self.result[f'{p}_rtot'] = {'time' : time, 'data' : rtot}

    def cwd_calc(self):
        """
        This method returns annual maximum consecutive wet days as requested by periods.
        """
        for p in self.period:
            time, data, _ = self.get_data(p)
            data = [np.where(data_ >= 1., 1., 0.) for data_ in data]
            for i in range(len(data)):
                for j in range(1, data[i].shape[0]):
                    data[i][j] = (data[i][j-1] + data[i][j]) * data[i][j]
            cwd = np.array([np.nanmax(data_, axis=0) for data_ in data])
            cwd[cwd == 0.] = np.nan
            self.result[f'{p}_cwd'] = {'time' : time, 'data' : cwd}

    def cdd_calc(self):
        """
        This method returns annual maximum consecutive dry days as requested by periods.
        """
        for p in self.period:
            time, data, _ = self.get_data(p)
            data = [np.where(data_ >= 1., 0., 1.) for data_ in data]
            for i in range(len(data)):
                for j in range(1, data[i].shape[0]):
                    data[i][j] = (data[i][j-1] + data[i][j]) * data[i][j]
            cdd = np.array([np.nanmax(data_, axis=0) for data_ in data])
            cdd[cdd == 0.] = np.nan
            self.result[f'{p}_cdd'] = {'time' : time, 'data' : cdd}

    def first_day(self, condition):
        if np.any(condition):
            return np.arange(condition.shape[0])[condition][0]
        else:
            return np.nan

    def firstHday_calc(self, H):
        """
        This method returns annual maximum as requested by periods and for "D" days of accumulation.
        """
        for p in self.period:
            time, data, _ = self.get_data(p)
            firstHday = np.array([np.apply_along_axis(func1d=self.first_day, arr=np.nancumsum(data_, axis=0) > H, axis=0) for data_ in data])
            self.result[f'{p}_first{H}day'] = {'time' : time, 'data' : firstHday}

    def sorted_max_calc(self, n=3):
        """
        This method returns annual n maximum values as requested by periods.
        """
        def _1D(arr):
            aux = np.flip(np.sort(arr[~np.isnan(arr)]))[:n]
            if aux.shape[0] == n:
                return aux
            else:
                return np.full((n,), np.nan)
        for p in self.period:
            time, data, q_95 = self.get_data(p)
            sorted_max = list()
            time_ = list()
            for i, data_ in enumerate(data):
                sorted_max.append(np.apply_along_axis(_1D, 0, data_))
                time_.append(time[i])
            self.result[f'{p}_{n}_sorted_rx1day'] = {'time' : np.array(time_), 'data' : np.array(sorted_max)}

class Rain_Gauge(Rainfall_Indices):
    """
    This class runs a pre-process for rain gauge data.

    Parameters:

    - path_csv : path string, dtype=str
        Path to csv file user wants to use. Default None.
    """
    def __init__(self, path_csv=None):
        if path_csv != None:
            with open(path_csv, 'r', newline='') as csvfile:
                data = np.array([_ for _ in csv.reader(csvfile, delimiter=',')])
            self.id, self.name, self.lon, self.lat, self.elevation, self.province, self.country, self.institution, self.record_time = data[:9, 1]
            self.lon, self.lat, self.elevation = float(self.lon), float(self.lat), float(self.elevation)
            self.time = np.array([datetime.datetime.strptime(str(_), '%Y-%m-%d') for _ in data[10:, 0]])
            self.data = data[10:, 1].astype('f')

    @staticmethod
    def detect_start_month(dt, prec):
        """
        This method returns start_month of the hydrological year.
        It's based in the relation between annual maximum of the month and maximum of the year.
        """
        def get_month(data, months):
            if np.all(np.isnan(data)):
                return np.nan
            else:
                return months[data == np.nanmax(data)][0]
        def _1D(res, months):
            res = res[~np.isnan(res)]
            freq = sp.relfreq(res, numbins=12, defaultreallimits=(0.5, 12.5))[0]
            months = np.flip(months[np.argsort(freq)])
            freq = np.flip(freq[np.argsort(freq)])
            max_month = int(months[0])
            prev_, next_ = adjacent_months(max_month)
            if freq[months == next_] >= freq[months == prev_]:
                return adjacent_months(max_month, 5)[0]
            else:
                return adjacent_months(max_month, 6)[0]
        months = np.arange(1, 13)
        rainfall_indices = Rainfall_Indices(dt, prec, period=['M'], start_month=1)
        rainfall_indices.rxDday_calc(1)
        dt_, data = Rain_Gauge.trim_data_yearly(
            rainfall_indices.result['M_rx1day']['time'], rainfall_indices.result['M_rx1day']['data'], start_month=1
        )
        data_cut = Rain_Gauge.cut_data_yearly(dt_, data, start_month=1)
        res = np.array([np.apply_along_axis(func1d=get_month, axis=0, arr=year_data, months=months) for year_data in data_cut[1]])
        return np.apply_along_axis(func1d=_1D, axis=0, arr=res, months=months)

    @staticmethod
    def get_indexes(year, month, years, months, start_month):
        """
        This method returns the indexes of year in years and month in months.
        """
        if month < start_month:
            year += 1
        aux_years = years == year
        aux_months = months == month
        return aux_years * aux_months
    
    def year_filter(self, y, years, months):
        """
        This method returns True if all data is less than 1.
        """
        prec_year = self.data[np.any([self.get_indexes(y, m, years, months, self.start_month) for m in range(1, 13)], axis=0)]
        prec_year = np.where(prec_year >= 1, prec_year, 0)
        if np.all(prec_year == 0):
            return True
        else:
            return False

    def discard_incomplete_years(self, delete_years):
        """
        This method filters years with all values less than 1 and years in delete_years list.
        """
        rainfall_indices = Rainfall_Indices(self.time, self.data, period=['Y'], start_month=self.start_month)
        rainfall_indices.calculate()
        years = np.array([_.year for _ in self.time])
        months = np.array([_.month for _ in self.time])
        months_ = np.arange(self.start_month, self.start_month + 12)
        months_[months_ > 12] -= 12
        years_ = np.unique(years)
        if self.start_month != 1:
            years_ = years_[:-1]
        for y in years_:
            if self.year_filter(y, years, months):
                self.data[np.any([self.get_indexes(y, m, years, months, self.start_month) for m in months_], axis=0)] = np.nan
            elif y in delete_years:
                self.data[np.any([self.get_indexes(y, m, years, months, self.start_month) for m in months_], axis=0)] = np.nan

    def preprocess(self, delete_years):
        """
        This method preprocess data. First, it gets start_month from detect_start_month method.
        Then, it uses trim_data_yearly inherited from Rainfall_Indices. Finally, it filters years without data
        and years specified in delete_years list.
        """
        self.start_month = self.detect_start_month(self.time, self.data)
        self.time, self.data = self.trim_data_yearly(self.time, self.data, self.start_month)
        self.discard_incomplete_years(delete_years)

    def save(self, path_csv):
        """
        This method saves all information to .csv file with provided path.
        """
        with open(path_csv, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',')
            csvwriter.writerow(['id', self.id])
            csvwriter.writerow(['name', self.name])
            csvwriter.writerow(['lon', self.lon])
            csvwriter.writerow(['lat', self.lat])
            csvwriter.writerow(['elevation', self.elevation])
            csvwriter.writerow(['province/state', self.province])
            csvwriter.writerow(['country', self.country])
            csvwriter.writerow(['institution', self.institution])
            csvwriter.writerow(['record_time', self.record_time])
            csvwriter.writerow(['start_month', self.start_month])
            csvwriter.writerow(['time', 'prec (mm)'])
            for i in range(self.time.shape[0]):
                csvwriter.writerow([self.time[i].date(), self.data[i]])

    def load(self, path_csv):
        """
        This method loads all information from .csv file with provided path.
        """
        if path_csv != None:
            with open(path_csv, 'r', newline='') as csvfile:
                data = np.array([_ for _ in csv.reader(csvfile, delimiter=',')])
            self.id, self.name, self.lon, self.lat, self.elevation, self.province, self.country, self.institution, self.record_time = data[:9, 1]
            self.lon, self.lat, self.elevation = float(self.lon), float(self.lat), float(self.elevation)
            self.start_month = int(data[9, 1])
            self.time = np.array([datetime.datetime.strptime(str(_), '%Y-%m-%d') for _ in data[11:, 0]])
            self.data = data[11:, 1].astype('f')
