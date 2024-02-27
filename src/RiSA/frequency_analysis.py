"""
This module is used for frequency analysis of hydrological data.
"""

# Libraries

import pymannkendall
import pyhomogeneity
import scipy.stats

from collections import namedtuple

from .basics import *

# Functions

def weibull_distribution(data):
    """
    Find Weibull's distribution frequencies for data from a numpy.array.

    Interagency Advisory Committee on Water Data. (1981).
    Guidelines For Determining Flood Flow Frequency, Bulletin #17B.
    (U. G. Survey, Ed.) Reston, Virginia: Office of Water Data Coordination.
    Obtenido de https://water.usgs.gov/osw/bulletin17b/dl_flow.pdf
    """
    data = data[~np.isnan(data)]
    data = np.flip(np.sort(data))
    rank = np.array([i for i in range(1, data.shape[0] + 1)])
    prob = rank / (data.shape[0] + 1)
    return data, 1 / prob

def chi2(obs, cdf, n_params):
    """
    Chi Square Goodness of Fit test. "obs" and "est" are
    the observed and estimated values.
    It returns the statistic and the p-value of the test.
    "obs" and "est" must be numpy.array both.
    """
    if len(obs) < 20:
        return np.nan
    elif len(obs) < 50:
        n_min = 5
        n_ = 10
    elif len(obs) < 100:
        n_min = 10
        n_ = 20
    else:
        n_min = np.floor(obs.shape[0] ** 2)
        n_ = np.ceil(obs.shape[0] / 5)
    f_obs = np.histogram(
        obs, bins=n_,
        range=(np.min(obs, axis=0) * 0.99, np.max(obs, axis=0) * 1.01),
    )
    f_est = np.array(
        [cdf([f_obs[1][1]])[0]] + \
        [
            cdf([f_obs[1][i+1]])[0] - cdf([f_obs[1][i]])[0]
            for i in range(1, f_obs[0].shape[0] - 1)
        ] + [1 - cdf([f_obs[1][-2]])[0]]
    )
    while np.any(f_est == 0) and n_ > n_min:
        n_    = n_ - 1
        f_obs = np.histogram(
            obs, bins=n_,
            range=(np.min(obs, axis=0) * 0.99, np.max(obs, axis=0) * 1.01),
        )
        f_est = np.array(
            [cdf([f_obs[1][1]])[0]] + \
            [
                cdf([f_obs[1][i+1]])[0] - cdf([f_obs[1][i]])[0]
                for i in range(1, f_obs[0].shape[0] - 1)
            ] + [1 - cdf([f_obs[1][-2]])[0]]
        )
    return scipy.stats.chisquare(
        f_obs[0], f_est * len(obs), ddof=n_params
    )[1]

def frequency_analysis(indices, replace=None):
    key_ = 'Y_rx1day'
    out_k = 'outliers'
    # Outliers
    out_f = Statictical_Tests.outliers_bulletin17b
    if replace is not None:
        indices.result[key_][out_k] = out_f(
            indices.result['Y_3_sorted_rx1day']['data'], replace=replace,
        )
    else:
        indices.result[key_][out_k] = out_f(indices.result[key_]['data'])
    indices.result[key_][out_k]['replace'] = replace
    w_out = indices.result[key_][out_k]['data_without_outliers'][-1]
    # Statistical Tests
    tests = Statictical_Tests(w_out, axis=0)
    tests.calculate()
    indices.result[key_]['data_outliers_tests'] = tests.result
    tests = Statictical_Tests(indices.result[key_]['data'], axis=0)
    tests.calculate()
    indices.result[key_]['data_tests'] = tests.result
    # Frecuency Analysis
    indices.result[key_]['lognorm'] = LogNormal_MV(w_out)
    # Probable Maximum Precipitation
    mean = np.nanmean(indices.result[key_]['data'])
    std = np.nanstd(indices.result[key_]['data'])
    indices.result[key_]['data_mean'] = mean
    indices.result[key_]['data_std'] = std
    indices.result[key_]['phi_pmp'] = 5.2253 * np.exp(1.958 * std / mean)
    indices.result[key_]['pmp'] = mean + std * indices.result[key_]['phi_pmp']
    return indices

def freq_conditions(indices, w_out=True):
    key_ = 'Y_rx1day'
    out_k = 'outliers'
    if w_out:
        data = indices.result[key_][out_k]['data_without_outliers'][-1]
        key_ = 'data_outliers_tests'
    else:
        data = indices.result[key_]['data']
        key_ = 'data_tests'
    iWW = int(indices.result[key_][key_]['iWW']['index']) >= 3
    hPE = int(indices.result[key_][key_]['hPE']['index']) >= 3
    tMK = int(indices.result[key_][key_]['tMK']['index'][0]) == 2
    return minimum_lenght(data, 14) * iWW * hPE * tMK

# Classes
class Statictical_Tests:
    """ 
    Get results of tests for the time serie.
    Runs a list of tests to a ndarray along the given axis.
    Inputs:
        - data: numpy.array.
        - without_outliers: default is True. If False is set,
            next tests are executed without taking out the outliers.
        - iAN: default is True for independence_wald_wolfowitz
            to be applied.
        - tMK: default is True for trend_mann_kendall to be applied.
        - sWI: default is True for signed_rank_wilcoxon to be applied.
        - sWI: default is True for homogeneity_pettitt to be applied.
    """
    def __init__(
            self, data, axis=0, iWW=True,
            tMK=True, hWI=False, hMW=False, hPE=True,
    ):
        if axis != 0:
            self.data = self.reshape_data(np.array(data), axis)
        else:
            self.data = np.array(data)
        self.iWW = iWW
        self.tMK = tMK
        self.hWI = hWI
        self.hMW = hMW
        self.hPE = hPE
        self.result = dict()

    def calculate(self):
        if self.iWW:
            self.result['iWW'] = self.independence_wald_wolfowitz(self.data)
        if self.tMK:
            self.result['tMK'] = self.trend_mann_kendall(self.data)
        if self.hWI:
            self.result['hWI'] = self.homogeneity_wilcoxon(self.data)
        if self.hMW:
            self.result['hMW'] = self.homogeneity_mann_whitney(self.data)
        if self.hPE:
            self.result['hPE'] = self.homogeneity_pettitt(self.data)

    @staticmethod
    def reshape_data(data, axis):
        axes = [i for i in range(len(data.shape))]
        axes.remove(axis)
        return np.transpose(data, axes=[axis] + axes)

    @staticmethod
    def outliers_bulletin17b(data, replace=None):
        """ Apply outliers test to a ndarray.

        Interagency Advisory Committee on Water Data. (1981). Guidelines For Determining Flood Flow Frequency, Bulletin #17B.
        (U. G. Survey, Ed.) Reston, Virginia: Office of Water Data Coordination.
        https://water.usgs.gov/osw/bulletin17b/dl_flow.pdf
        """
        def _1Dtest(data):
            K = np.array([[10, 2.036],[11, 2.088],[12, 2.134],[13, 2.175],\
                [14, 2.213],[15, 2.247],[16, 2.279],[17, 2.309],[18, 2.335],\
                [19, 2.361],[20, 2.385],[21, 2.408],[22, 2.429],[23, 2.448],\
                [24, 2.467],[25, 2.486],[26, 2.502],[27, 2.519],[28, 2.534],\
                [29, 2.549],[30, 2.563],[31, 2.577],[32, 2.591],[33, 2.604],\
                [34, 2.616],[35, 2.628],[36, 2.639],[37, 2.65],[38, 2.661],\
                [39, 2.671],[40, 2.682],[41, 2.692],[42, 2.7],[43, 2.71],\
                [44, 2.719],[45, 2.727],[46, 2.736],[47, 2.744],[48, 2.753],\
                [49, 2.76],[50, 2.768],[51, 2.7752],[52, 2.7824],[53, 2.7896],\
                [54, 2.7968],[55, 2.804],[56, 2.8106],[57, 2.8172],[58, 2.8238],\
                [59, 2.8304],[60, 2.837],[61, 2.8428],[62, 2.8486],[63, 2.8544],\
                [64, 2.8602],[65, 2.866],[66, 2.8714],[67, 2.8768],[68, 2.8822],\
                [69, 2.8876],[70, 2.893],[71, 2.8978],[72, 2.9026],[73, 2.9074],\
                [74, 2.9122],[75, 2.917],[76, 2.9216],[77, 2.9262],[78, 2.9308],\
                [79, 2.9354],[80, 2.94],[81, 2.9442],[82, 2.9484],[83, 2.9526],\
                [84, 2.9568],[85, 2.961],[86, 2.965],[87, 2.969],[88, 2.973],\
                [89, 2.977],[90, 2.981],[91, 2.9848],[92, 2.9886],[93, 2.9924],\
                [94, 2.9962],[95, 3],[96, 3.0034],[97, 3.0068],[98, 3.0102],\
                [99, 3.0136],[100, 3.017],[101, 3.0202],[102, 3.0234],[103, 3.0266],\
                [104, 3.0298],[105, 3.033],[106, 3.0362],[107, 3.0394],[108, 3.0426],\
                [109, 3.0458],[110, 3.049],[111, 3.0519],[112, 3.0548],[113, 3.0577],\
                [114, 3.0606],[115, 3.0635],[116, 3.0664],[117, 3.0693],[118, 3.0722],\
                [119, 3.0751],[120, 3.078],[121, 3.0806],[122, 3.0832],[123, 3.0858],\
                [124, 3.0884],[125, 3.091],[126, 3.0936],[127, 3.0962],[128, 3.0988],\
                [129, 3.1014],[130, 3.104],[131, 3.1065],[132, 3.109],[133, 3.1115],\
                [134, 3.114],[135, 3.1165],[136, 3.119],[137, 3.1215],[138, 3.124],\
                [139, 3.1265],[140, 3.129]])
            log_data = np.log(np.where(data > 0, data, np.nan))
            n = data[~np.isnan(log_data)].shape[0]
            skew = scipy.stats.stats.skew(data, nan_policy='omit')
            if skew < -0.4:
                ll = np.nanmean(log_data) - K[K[:, 0] == n, 1] * np.nanstd(log_data)
                low_outliers = np.where(log_data < ll, data, np.nan)
                log_data[log_data < ll] = np.nan
                ul = np.nanmean(log_data) + K[K[:, 0] == n, 1] * np.nanstd(log_data)
                high_outliers = np.where(log_data > ul, data, np.nan)
                log_data[log_data > ul] = np.nan
            elif skew > 0.4:
                ul = np.nanmean(log_data) + K[K[:, 0] == n, 1] * np.nanstd(log_data)
                high_outliers = np.where(log_data > ul, data, np.nan)
                log_data[log_data > ul] = np.nan
                ll = np.nanmean(log_data) - K[K[:, 0] == n, 1] * np.nanstd(log_data)
                low_outliers = np.where(log_data < ll, data, np.nan)
                log_data[log_data < ll] = np.nan
            else:
                ul = np.nanmean(log_data) + K[K[:, 0] == n, 1] * np.nanstd(log_data)
                ll = np.nanmean(log_data) - K[K[:, 0] == n, 1] * np.nanstd(log_data)
                high_outliers = np.where(log_data > ul, data, np.nan)
                low_outliers = np.where(log_data < ll, data, np.nan)
                log_data[log_data < ll] = np.nan
                log_data[log_data > ul] = np.nan
            return (
                high_outliers, low_outliers,
                np.where(~np.isnan(log_data), data, np.nan),
                np.exp(ul), np.exp(ll),
            )
        def replace_function(test, out_replace):
            w_out = test[2]
            w_out[~np.isnan(test[0])] = out_replace[~np.isnan(test[0])]
            return test[0], test[1], w_out, test[3], test[4]
        data = np.array(data)
        if replace is not None:
            data_ = data[:, 0]
            res = list()
            for i in range(replace):
                res.append(replace_function(_1Dtest(data_), data[:, i+1]))
                data_ = res[-1][2]
                if np.all(np.isnan(res[-1][0])):
                    break
        else:
            if len(data.shape) > 1:
                raise Exception('This test is only for 1D arrays.')
            res = [_1Dtest(data)]
        return {
            'high_outliers' : np.array([_[0] for _ in res]),
            'low_outliers' : np.array([_[1] for _ in res]),
            'data_without_outliers' : np.array([_[2] for _ in res]),
            'high_limit' : np.array([_[3] for _ in res]),
            'low_limit' : np.array([_[4] for _ in res]),
        }

    @staticmethod
    def independence_wald_wolfowitz(data):
        """Apply Wald-Wolfowitz's independence test to a ndarray.

        Wald, A., & Wolfowitz, J. (1943).
        An Exact Test for Randomness in the Non-Parametric Case 
        Based on Serial Correlation.
        The Annals of Mathematical Statistics, 14(4), 378-388.
        http://www.jstor.org/stable/2235925

        Returns result for a two-sided normal distribution.
        """
        def p_(x):
            x = x[~np.isnan(x)]
            N = x.shape[0]
            R = np.sum([
                x[i] * x[i+1] for i in range(N - 1)
            ]) + x[0] * x[-1]
            s1 = np.sum(x**1)
            s2 = np.sum(x**2)
            s3 = np.sum(x**3)
            s4 = np.sum(x**4)
            E_R = (s1**2 - s2) / (N - 1)
            Var_R = (s2**2 - s4) / (N - 1) + (
                s1**4 - 4 * s1**2 * s2 + 4 * s1 * s3 + s2**2 - 2 * s4
            ) / ((N - 1) * (N - 2)) - E_R**2
            Z = (R - E_R) / Var_R**0.5
            return scipy.stats.norm.cdf(np.abs(Z))
        data = np.array(data)
        p = np.apply_along_axis(func1d=p_, axis=0, arr=data)
        res = np.full(p.shape, fill_value='pass 95%')
        aux = np.full(p.shape, fill_value=3)
        res[p > 0.975] = 'pass 99%'
        aux[p > 0.975] = 2
        res[p > 0.995] = 'not pass'
        aux[p > 0.995] = 1
        return {'index' : aux, 'result' : res, 'p_value' : p}

    @staticmethod
    def trend_mann_kendall(data):
        """Apply Mann Kendall's trend test,
        the Hamed-Rao modification, the pre whitening modification,
        the trend free pre whitening modification and the calculation
        of the sens slope to a 1 dimension ndarray.
        https://github.com/mmhs013/pymannkendall
        Output:
            dictionary with the next keys:
                - Name
                - Autocorrelation lag 1 with trend
                - Autocorrelation lag 1 without trend
                - Normal confidence interval
                - MK
                - MK-HR
                - MK-PW
                - MK-TF-PW
                - SS
        Citation:
        Hussain et al., (2019). pyMannKendall: a python package for
        non parametric Mann Kendall family of trend tests.. 
        Journal of Open Source Software, 4(39), 1556,
        https://doi.org/10.21105/joss.01556
        """
        def confidence_sens_slope(x, var_s, alpha):
            """Confidence interval for Sen's slope.
            """
            idx = 0
            n = len(x)
            d = np.ones(int(n*(n-1)/2))
            for i in range(n-1):
                j = np.arange(i+1,n)
                d[idx : idx + len(j)] = (x[j] - x[i]) / (j - i)
                idx = idx + len(j)
            N = n*(n-1)/2
            C_alpha = scipy.stats.norm.ppf(1-alpha/2) * var_s ** 0.5
            M1 = (N - C_alpha) / 2
            M2 = (N + C_alpha) / 2
            return [
                np.interp(M1 - 1, np.arange(len(d)), np.sort(d)),
                np.interp(M2, np.arange(len(d)), np.sort(d)),
            ]
        def _1D_test(data):
            original = pymannkendall.original_test(data)
            # slope = pymannkendall.sens_slope(data)
            # slope_confidence = [confidence_sens_slope(data, original[6], 0.05), confidence_sens_slope(data, original[6], 0.01)]
            return (
                0,# sm.tsa.acf(data)[1],
                0,# sm.tsa.acf(data - np.arange(1, data.shape[0] + 1) * slope[0])[1],
                0,# scipy.stats.norm.ppf(1 - 0.05 / 2) / np.sqrt(data.shape[0]),
                0,# - scipy.stats.norm.ppf(1 - 0.05 / 2) / np.sqrt(data.shape[0]),
                original[0],
                pymannkendall.original_test(data, alpha=0.01)[0],
                0,# pymannkendall.hamed_rao_modification_test(data)[0],
                0,# pymannkendall.hamed_rao_modification_test(data, alpha=0.01)[0],
                0,# pymannkendall.pre_whitening_modification_test(data)[0],
                0,# pymannkendall.pre_whitening_modification_test(data, alpha=0.01)[0],
                0,# pymannkendall.trend_free_pre_whitening_modification_test(data)[0],
                0,# pymannkendall.trend_free_pre_whitening_modification_test(data, alpha=0.01)[0],
                0,# slope[0],
                0,# slope[1],
                0,# slope_confidence[0][0],
                0,# slope_confidence[1][0],
                0,# slope_confidence[0][1],
                0,# slope_confidence[1][1],
            )
        result_reference = [
            # 'Autocorrelation_lag_1_with_trend', 'Autocorrelation_lag_1_without_trend',
            # 'Normal_lower', 'Normal_upper',
            'MK_95', 'MK_99',
            # 'MK_HR_95', 'MK_HR_99',
            # 'MK_PW_95', 'MK_PW_99',
            # 'MK_TF_PW_95', 'MK_TF_PW_99',
            # 'Slope', 'Intercept',
            # 'SS_95_lower', 'SS_99_lower',
            # 'SS_95_upper', 'SS_99_upper',
        ]
        if len(data.shape) > 1:
            if len(data.shape) > 2:
                res = np.array([
                    [
                        _1D_test(data[:, i, j])
                        for j in range(data.shape[2])
                    ]
                    for i in range(data.shape[1])
                ])
                res_ = res[:, :, 4:12]
            else:
                res = np.array([
                    _1D_test(data[:, i])
                    for i in range(data.shape[1])
                ])
                res_ = res[:, 4:12]
        else:
            res = np.array(_1D_test(data))
            res_ = res[4:12]
        return {
            'index' : np.where(
                res_ == 'increasing', 3,
                np.where(
                    res_ == 'decreasing', 1, 2,
                ),
            ),
            'result' : res, 'reference' : result_reference,
        }

    @staticmethod
    def homogeneity_wilcoxon(data):
        """Apply Wilcoxon's signed-rank test to a ndarray,
        in which data is split in two halves.

        Wilcoxon, F. (12, 1945). Individual Comparisons by Ranking Methods.
        Biometrics Bulletin, 1(6), 80-83. https://www.jstor.org/stable/3001968
        """
        def _1Dtest(data):
            data = data[~np.isnan(data)]
            if data.shape[0] % 2 == 0:
                i = int(data.shape[0] / 2)
                x, y = data[:i], data[i:]
            else:
                i = int((data.shape[0] - 1) / 2)
                x, y = data[:i], data[i:-1]
            _, p_value = scipy.stats.wilcoxon(x, y, axis=0)
            if p_value < 0.01:
                return [1, 'not pass']
            elif p_value < 0.05:
                return [2, 'pass 99%']
            else:
                return [3, 'pass 95%']
        data = np.array(data)
        res = np.apply_along_axis(_1Dtest, 0, data)
        return {'index' : res[0], 'result' : res[1]}
    
    @staticmethod
    def homogeneity_mann_whitney(data):
        """Apply Mann-Whitney (1947) test, in which data is divided
        in paired intervals of different lenghts.
        It returns the lower p-value of all and an estimated change
        point based on its position.

        Mann, H. B. and Whitney, D. R. (1947). On a Test of Whether
        one of Two Random Variables is Stochastically Larger than the Other.
        The Annals of Mathematical Statistics , Mar., 1947, Vol. 18,
        No. 1 (Mar., 1947), pp. 50-60. Institute of Mathematical Statistics.
        https://www.jstor.org/stable/2236101.
        """
        def _1Dtest(data):
            data = data[~np.isnan(data)]
            res = np.array([
                scipy.stats.mannwhitneyu(data[:i], data[i:], axis=0)
                for i in range(1, data.shape[0])
            ])
            p_value = np.min(res[:, 1])
            cp = np.arange(1, data.shape[0])[res[:, 1] == p_value][0]
            if p_value < 0.01:
                return [1, 'not pass', cp]
            elif p_value < 0.05:
                return [2, 'pass 99%', cp]
            else:
                return [3, 'pass 95%', cp]
        data = np.array(data)
        res = np.apply_along_axis(_1Dtest, 0, data)
        return {
            'index' : res[0],
            'result' : res[1],
            'change_point' : res[2]
        }

    @staticmethod
    def homogeneity_pettitt(data, sim=100):
        """Apply Pettitt's test to a ndarray.

        Pettitt, A. N. (1979). A Non-parametric
        Approach to the Change-point Problem.
        Journal of the Royal Statistical Society.
        Series C (Applied Statistics), 28(2), 126-135.
        http://www.jstor.org/stable/2346729
        """
        def _1Dtest(x):
            result95 = pyhomogeneity.pettitt_test(
                x, alpha=0.05, sim=sim,
            )
            # result99 = pyhomogeneity.pettitt_test(x, alpha=0.01, sim=sim)
            # if result99[0]:
            #     return [1, 'not pass', result99[1], result99[4][0], result99[4][1]]
            # elif result95[0]:
            #     return [2, 'pass 99%', result95[1], result95[4][0], result95[4][1]]
            # else:
            #     return [3, 'pass 95%', result95[1], result95[4][0], result95[4][1]]
            if result95[0]:
                return [
                    1, 'not pass', result95[1],
                    result95[4][0], result95[4][1],
                ]
            else:
                return [
                    3, 'pass 95%', result95[1],
                    result95[4][0], result95[4][1],
                ]
        data = np.array(data)
        res = np.apply_along_axis(_1Dtest, 0, data)
        return {
            'index' : res[0], 'result' : res[1],
            'change_point' : res[2],
            'mean_1' : res[3], 'mean_2' : res[4]
        }

class LogNormal_MV:
    """Distribución LogNormal de 3 parámetros estimados por Máxima Verosimilitud.

    Preparado para el análisis de datos provenientes de precipitaciones máximas anuales

    "pdf"
    - Obtiene los valores de la curva de densidad de probabilidad de los "x" dados.

    "ppf"
    - Obtiene los valores de la curva de frecuencias para los periodos de retorno "T" dados.
    """
    def __init__(self, data):
        self.sorted_data, self.return_period = weibull_distribution(data)
        self.n = data.shape[0]
        self.params = scipy.stats.lognorm.fit(self.sorted_data, floc=0)
    def pdf(self, x):
        return scipy.stats.lognorm.pdf(
            x, self.params[0], loc=self.params[1], scale=self.params[2],
        )
    def cdf(self, x):
        return scipy.stats.lognorm.cdf(
            x, self.params[0], loc=self.params[1], scale=self.params[2],
        )
    def ppf(self, T):
        if type(T) == list:
            T = np.array(T)
        try:
            fi = 2.584458*np.log(T) ** (3/8) - 2.252573
            conf = self.params[0] / np.sqrt(self.n) * np.sqrt(1 + (fi ** 2) / 2)
            ppf_mean = scipy.stats.lognorm.ppf(
                1 - 1/T, self.params[0],
                loc=self.params[1], scale=self.params[2]
            )
            ppf_low  = np.exp(np.log(ppf_mean) - 1.96 * conf)
            ppf_high = np.exp(np.log(ppf_mean) + 1.96 * conf)
            return ppf_low, ppf_mean, ppf_high
        except:
            print('The type of "T" must be numpy.array or list.')
    def goodness_fit(self):
        result_goodness_fit = namedtuple(
            'Goodness_of_Fit',
            [
                'Kolmogorov_Smirnov_pvalue', 'Chi_Square_pvalue',
                'Root_Mean_Squared_Error', 'Percentage_error'
            ]
        )
        return result_goodness_fit(
            scipy.stats.kstest(self.sorted_data, self.cdf)[1],
            chi2(self.sorted_data, self.cdf, 3),
            root_mean_squared_error(
                self.sorted_data, self.ppf(self.return_period)[1],
            ),
            percentage_error(
                self.sorted_data, self.ppf(self.return_period)[1],
                _abs=False,
            ),
        )

class GEV_MV:
    """Distribución Generalized Extreme Value de 3 parámetros estimados por Máxima Verosimilitud.

    Preparado para el análisis de datos provenientes de precipitaciones máximas anuales

    "pdf"
    - Obtiene los valores de la curva de densidad de probabilidad de los "x" dados.

    "ppf"
    - Obtiene los valores de la curva de frecuencias para los periodos de retorno "T" dados.
    """
    def __init__(self, data):
        self.sorted_data, self.return_period = weibull_distribution(data)
        self.n = data.shape[0]
        self.params = scipy.stats.genextreme.fit(self.sorted_data)
        self.stats  = scipy.stats.genextreme.stats(
            self.params[0], loc=self.params[1],
            scale=self.params[2], moments='mvsk',
        )
    def pdf(self, x):
        return scipy.stats.genextreme.pdf(
            x, self.params[0], loc=self.params[1], scale=self.params[2],
        )
    def cdf(self, x):
        return scipy.stats.genextreme.cdf(
            x, self.params[0], loc=self.params[1], scale=self.params[2],
        )
    def ppf(self, T):
        if type(T) == list:
            T = np.array(T)
        try:
            conf = np.sqrt(self.stats[1] / self.n) * \
                np.sqrt(1.11 + 0.52 * (-np.log(-np.log(1 - 1 / T))) + \
                0.61 * (-np.log(-np.log(1 - 1 / T))) ** 2)
            ppf_mean = scipy.stats.genextreme.ppf(
                1 - 1/T, self.params[0],
                loc=self.params[1], scale=self.params[2],
            )
            ppf_low  = ppf_mean - 1.96 * conf
            ppf_high = ppf_mean + 1.96 * conf
            return ppf_low, ppf_mean, ppf_high
        except:
            print('The type of "T" must be numpy.array or list.')
    def goodness_fit(self):
        result_goodness_fit = namedtuple(
            'Goodness_of_Fit',
            [
                'Kolmogorov_Smirnov_pvalue', 'Chi_Square_pvalue',
                'Root_Mean_Squared_Error', 'Percentage_error'
            ]
        )
        return result_goodness_fit(
            scipy.stats.kstest(self.sorted_data, self.cdf)[1],
            chi2(self.sorted_data, self.cdf, 3),
            root_mean_squared_error(
                self.sorted_data, self.ppf(self.return_period)[1],
            ),
            percentage_error(
                self.sorted_data, self.ppf(self.return_period)[1],
                _abs=False,
            ),
        )

class GEV_MM:
    """Distribución Generalized Extreme Value de 3 parámetros estimados por el Método de los Momentos.

    Preparado para el análisis de datos provenientes de precipitaciones máximas anuales

    "pdf"
    - Obtiene los valores de la curva de densidad de probabilidad de los "x" dados.

    "ppf"
    - Obtiene los valores de la curva de frecuencias para los periodos de retorno "T" dados.
    """
    def __init__(self, data):
        self.sorted_data, self.return_period = weibull_distribution(data)
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        self.n = data.shape[0]
        # Coeficiente de asimetría de la muestra (skew)
        g = 0  
        for i in range(self.n):
          g = g + self.n * (data[i] - mean) ** 3
        g = g / ((self.n - 1) * (self.n - 2) * std ** 3)
        # Expresiones para "beta" (c) parámetro de forma de la distribución
        if g > -11.35 and g < 1.1396:
            self.c = 0.279434 - 0.333535 * g + 0.048306 * g ** 2 - \
                0.023314 * g ** 3 + 0.00376 * g ** 4 - 0.000263 * g ** 5
        if g > 1.14 and g < 18.95:
            self.c = 0.25031 - 0.29219 * g + 0.075357 * g ** 2 - \
                0.010883 * g ** 3 + 0.000904 * g ** 4 - 0.000043 * g ** 5
        self.params = scipy.stats.genextreme.fit_loc_scale(
            self.sorted_data, self.c,
        )
        self.stats  = scipy.stats.genextreme.stats(
            self.c, loc=self.params[0], scale=self.params[1],
        )
    def pdf(self, x):
        return scipy.stats.genextreme.pdf(
            x, self.c, loc=self.params[0], scale=self.params[1],
        )
    def cdf(self, x):
        return scipy.stats.genextreme.cdf(
            x, self.c, loc=self.params[0], scale=self.params[1],
        )
    def ppf(self, T):
        if type(T) == list:
            T = np.array(T)
        try:
            conf = np.sqrt(self.stats[1] / self.n) * \
                np.sqrt(1.11 + 0.52 * (-np.log(-np.log(1 - 1 / T))) + \
                0.61 * (-np.log(-np.log(1 - 1 / T))) ** 2)
            ppf_mean = scipy.stats.genextreme.ppf(
                1 - 1/T, self.c, loc=self.params[0], scale=self.params[1],
            )
            ppf_low  = ppf_mean - 1.96 * conf
            ppf_high = ppf_mean + 1.96 * conf
            return ppf_low, ppf_mean, ppf_high
        except:
            print('The type of "T" must be numpy.array or list.')
    def goodness_fit(self):
        result_goodness_fit = namedtuple(
            'Goodness_of_Fit',
            [
                'Kolmogorov_Smirnov_pvalue', 'Chi_Square_pvalue',
                'Root_Mean_Squared_Error', 'Percentage_error'
            ]
        )
        return result_goodness_fit(
            scipy.stats.kstest(self.sorted_data, self.cdf)[1],
            chi2(self.sorted_data, self.cdf, 2),
            root_mean_squared_error(
                self.sorted_data, self.ppf(self.return_period)[1],
            ),
            percentage_error(
                self.sorted_data, self.ppf(self.return_period)[1],
                _abs=False,
            ),
        )

class Gumbel_MV:
    """Distribución Gumbel de 2 parámetros estimados por Máxima Verosimilitud.

    Preparado para el análisis de datos provenientes de precipitaciones máximas anuales.

    "pdf"
    - Obtiene los valores de la curva de densidad de probabilidad de los "x" dados.

    "ppf"
    - Obtiene los valores de la curva de frecuencias para los periodos de retorno "T" dados.
    """
    def __init__(self, data):
        self.sorted_data, self.return_period = weibull_distribution(data)
        self.n = data.shape[0]
        self.params = scipy.stats.gumbel_r.fit(self.sorted_data)
    def pdf(self, x):
        return scipy.stats.gumbel_r.pdf(
            x, loc=self.params[0], scale=self.params[1],
        )
    def cdf(self, x):
        return scipy.stats.gumbel_r.cdf(
            x, loc=self.params[0], scale=self.params[1],
        )
    def ppf(self, T):
        if type(T) == list:
            T = np.array(T)
        try:
            fi = (- np.sqrt(6) / np.pi) * \
                (0.5772 + np.log(np.log(T / (T - 1))))
            conf = np.sqrt(self.params[1]) / np.sqrt(self.n) * \
                np.sqrt(1 + 1.1396 * fi + 1.1 * fi ** 2)
            ppf_mean = scipy.stats.gumbel_r.ppf(
                1 - 1/T, loc=self.params[0], scale=self.params[1],
            )
            ppf_low  = ppf_mean - 1.96 * conf
            ppf_high = ppf_mean + 1.96 * conf
            return ppf_low, ppf_mean, ppf_high
        except:
            print('The type of "T" must be numpy.array or list.')
    def goodness_fit(self):
        result_goodness_fit = namedtuple(
            'Goodness_of_Fit',
            [
                'Kolmogorov_Smirnov_pvalue', 'Chi_Square_pvalue',
                'Root_Mean_Squared_Error', 'Percentage_error',
            ],
        )
        return result_goodness_fit(
            scipy.stats.kstest(self.sorted_data, self.cdf)[1],
            chi2(self.sorted_data, self.cdf, 3),
            root_mean_squared_error(
                self.sorted_data, self.ppf(self.return_period)[1],
            ),
            percentage_error(
                self.sorted_data, self.ppf(self.return_period)[1],
                _abs=False,
            ),
        )

class Gumbel_MM:
    """Distribución Gumbel de 2 parámetros estimados por el Método de los Momentos.

    Preparado para el análisis de datos provenientes de precipitaciones máximas anuales.

    "pdf"
    - Obtiene los valores de la curva de densidad de probabilidad de los "x" dados.

    "ppf"
    - Obtiene los valores de la curva de frecuencias para los periodos de retorno "T" dados.
    """
    def __init__(self, data):
        self.sorted_data, self.return_period = weibull_distribution(data)
        self.n = data.shape[0]
        self.params = scipy.stats.gumbel_r.fit_loc_scale(self.sorted_data)
    def pdf(self, x):
        return scipy.stats.gumbel_r.pdf(
            x, loc=self.params[0], scale=self.params[1],
        )
    def cdf(self, x):
        return scipy.stats.gumbel_r.cdf(
            x, loc=self.params[0], scale=self.params[1],
        )
    def ppf(self, T):
        if type(T) == list:
            T = np.array(T)
        try:
            fi = (- np.sqrt(6) / np.pi) * \
                (0.5772 + np.log(np.log(T / (T - 1))))
            conf = np.sqrt(self.params[1]) / np.sqrt(self.n) * \
                np.sqrt(1 + 1.1396 * fi + 1.1 * fi ** 2)
            ppf_mean = scipy.stats.gumbel_r.ppf(
                1 - 1/T, loc=self.params[0], scale=self.params[1],
            )
            ppf_low  = ppf_mean - 1.96 * conf
            ppf_high = ppf_mean + 1.96 * conf
            return ppf_low, ppf_mean, ppf_high
        except:
            print('The type of "T" must be numpy.array or list.')
    def goodness_fit(self):
        result_goodness_fit = namedtuple(
            'Goodness_of_Fit',
            [
                'Kolmogorov_Smirnov_pvalue', 'Chi_Square_pvalue',
                'Root_Mean_Squared_Error', 'Percentage_error',
            ],
        )
        return result_goodness_fit(
            scipy.stats.kstest(self.sorted_data, self.cdf)[1],
            chi2(self.sorted_data, self.cdf, 2),
            root_mean_squared_error(
                self.sorted_data, self.ppf(self.return_period)[1],
            ),
            percentage_error(
                self.sorted_data, self.ppf(self.return_period)[1],
                _abs=False,
            ),
        )

class LogPearson3_MM:
    """Distribución LogPearson 3 de 3 parámetros estimados por el Método de los Momentos.

    Preparado para el análisis de datos provenientes de precipitaciones máximas anuales.

    "pdf"
    - Obtiene los valores de la curva de densidad de probabilidad de los "x" dados.

    "ppf"
    - Obtiene los valores de la curva de frecuencias para los periodos de retorno "T" dados.
    """
    def __init__(self, data):
        self.sorted_data, self.return_period = weibull_distribution(data)
        self.n = data.shape[0]
        self.params = scipy.stats.pearson3.fit(
            np.log10(self.sorted_data), method='MM',
        )
        self.stats = scipy.stats.pearson3.stats(
            self.params[0],
            loc=self.params[1], scale=self.params[2],
        )
        self.k = self.params[0] / 6
    def pdf(self, x):
        return scipy.stats.pearson3.pdf(
            np.log10(x), self.params[0],
            loc=self.params[1], scale=self.params[2],
        )
    def cdf(self, x):
        return scipy.stats.pearson3.cdf(
            np.log10(x), self.params[0],
            loc=self.params[1], scale=self.params[2],
        )
    def ppf(self, T):
        if type(T) == list:
            T = np.array(T)
        try:
            # Abramowitz y Stegun, 1965
            z      = list()
            for p in (1/T):
                if p > 0.5:
                    p = 1 - p
                    w = np.sqrt(np.log(1 / (p ** 2)))
                    z.append(
                        -(w - (
                            (2.515517 + 0.802853 * w + 0.010328 * w ** 2) \
                            / (1 + 1.432788 * w + 0.189269 * w ** 2 + 0.001308 * w **3)
                        ))
                    )
                else:
                    w = np.sqrt(np.log(1 / (p ** 2)))
                    z.append(w - ((2.515517 + 0.802853 * w + 0.010328 * w ** 2) \
                        / (1 + 1.432788 * w + 0.189269 * w ** 2 + 0.001308 * w **3)))
            z = np.array(z)
            # Wilson-Hilferty approximation, Kite 1977
            fi = z + (z ** 2 - 1) * self.k + 1/3 * (z ** 3 - 6 * z) * self.k ** 2 - \
                (z ** 2 - 1) * self.k ** 3 + z * self.k ** 4 + 1/3 * self.k ** 5
            a = 1 - (1.96 ** 2) / (2 * (self.n - 1))
            b = fi ** 2 - (1.96 ** 2) / self.n
            fi_U = (fi + np.sqrt(fi ** 2 - a * b)) / a
            fi_L = (fi - np.sqrt(fi ** 2 - a * b)) / a
            ppf_mean = 10 ** (self.stats[0] + fi   * np.sqrt(self.stats[1]))#scipy.stats.pearson3.ppf(1 - 1/T, self.params[0], loc=self.params[1], scale=self.params[2])
            ppf_low  = 10 ** (self.stats[0] + fi_L * np.sqrt(self.stats[1]))
            ppf_high = 10 ** (self.stats[0] + fi_U * np.sqrt(self.stats[1]))
            return ppf_low, ppf_mean, ppf_high
        except:
            print('The type of "T" must be numpy.array or list.')
    def goodness_fit(self):
        result_goodness_fit = namedtuple(
            'Goodness_of_Fit',
            [
                'Kolmogorov_Smirnov_pvalue', 'Chi_Square_pvalue',
                'Root_Mean_Squared_Error', 'Percentage_error',
            ],
        )
        return result_goodness_fit(
            scipy.stats.kstest(self.sorted_data, self.cdf)[1],
            chi2(self.sorted_data, self.cdf, 3),
            root_mean_squared_error(
                self.sorted_data, self.ppf(self.return_period)[1],
            ),
            percentage_error(
                self.sorted_data, self.ppf(self.return_period)[1],
                _abs=False,
            ),
        )
