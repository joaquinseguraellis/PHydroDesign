# PydroDesign

Test version.

0.0.11
	- Change in Precipitation_test class:
		- staticmethod trend_mann_kendall_DataArray change from 
		"return(da.name, 'Se acepta con una confianza del 95%.', 'No se observa tendencia.')" to 
		"return([da.name, 'Se acepta con una confianza del 95%.', 'No se observa tendencia.', result])".

		- "result" was added to all the return fuctions of trend_mann_kendall_DataArray.

		- __init__ change from
		"self.da_o, self.da_ = self.outliers_chow_DataArray(da)[:2]" to
		"self.da_o, self.da_, self.o_res = self.outliers_chow_DataArray(da)".

0.0.12
	- Change in Precipitation_test class:
		- added staticmethods:
			- trend_mann_kendall_DataArray_hamed_rao
			- trend_mann_kendall_DataArray_trend_free_pre_whitening
			- trend_mann_kendall_DataArray_sens_slope

0.0.13
	- Change in Precipitation_test class:
		- added 0 filter in independence_anderson_DataArray.

0.0.14
	- Change in Precipitation_test class:
		- change trend_mann_kendall_DataArray_pre_whitening to trend_mann_kendall_DataArray_trend_free_pre_whitening.
		- independence_anderson_DataArray is deactivated.
		- independence_wald_wolfowitz_DataArray work in progress.

0.0.15
	- Change in Precipitation_test class:
		- independence_anderson_DataArray is reactivated.
		- added if you want to applied the tests with or without outliers from outliers_chow_DataArray.

0.0.16
	- Change in Precipitation_test class:
		- added some options to choose whether a test is applied or not.
		- name of staticmethod signed_rank_wilcoxon change to signed_rank_wilcoxon_DataArray.
		- all Mann Kendall's tests were joined in a unique staticmethod replacing the staticmethod trend_mann_kendall_DataArray.
		- added the pre_whitening_modification_test to Mann Kendall's results.
	
	0.0.16.1 - 2
		- Error correction.

0.0.17
	- Change in Precipitation_test class:
		- added the posibility to use the independence_wald_wolfowitz_DataArray test.
	- Change in xarray_tools.py:
		- added Wald Wolfowitz's test for xarray.Dataset and a list of xarray.Dataset.
	
	0.0.17.1 - 2 - 3 - 4 - 5 - 6 - 7
		- Error correction.

0.0.18
	- Change in Precipitation_test class:
		- added the posibility to use the homogeneity_pettitt_DataArray test.
	- Change in xarray_tools.py:
		- added Pettitt's test for xarray.Dataset and a list of xarray.Dataset.
	
	0.0.18.1 - 2
		- Error correction.

0.0.19
	- Change in Precipitation_test class:
		- added 1% alpha for Mann Kendall's tests.

0.0.20
	- Change in Precipitation_test class:
		- added confidence intervals for Sen's slope in Mann Kendall's tests.
	
	0.0.20.1 - 2
		- Error correction.

0.0.21
	- Change in Precipitation_Analysis:
		- deleted the option to analize climate indexes for durations higher than a day.

0.0.22
	- Change in Precipitation_test_geo in geo_tools.py:
		- added multiprocessing python for better performance.
	
	0.0.22.1 - 2 - 3 - 4
		- Error correction.

0.0.23
	- Replaced save_map method for Savemap class.
	
	0.0.23.1 - 2 - 3 - 4 - 5 - 6
		- Error correction.

0.0.24
	- Change in geo_tools.py:
		- added a new class for getting IMERG maximums from an hdf5 file.
	
	0.0.24.1 - 2
		- Error correction.

0.0.25
	- Change in geo_tools.py:
		- added a new class for getting IMERG statistical tests reading from an hdf5 file.
	
	0.0.25.1 - 2 - 3
		- Error correction.

0.0.26
	- Change in geo_tools.py:
		- Savemap class change from receiving a xarray.Dataarray to a numpy.array and a numpy.array with longitude in index 0 and latitude in index 1.
	
	0.0.26.1 - 2 - 3
		- Error correction.
	
	0.0.26.4
		- Stop drawing lakes in maps.
	
	0.0.26.5
		- Error correction.

0.1.0
	- Total rework starts:
		- Deleted xarray_tools.py
		- hidro_tools.py: 
			- Precipitation_Analysis rework for receiving numpy.array objects and time with datetime library.
	
	0.1.0.1
		- Sweeping up the garbage.
	
	0.1.0.2
		- Error correction.

0.1.1
	- Rework of Precipitation_test class

0.1.2
	- Rework of Probability Distribution Functions classes
	
	0.1.2.1
		- Error correction.

0.1.3
	- geo_tools.py
		- Added the option to download IMERG Late product

0.1.4
	- Added some reviewed methods and classes.
	
	0.1.4.1
		- Error correction.
	
	0.1.4.2
		- Get sum from 0 to 0 for half hourly IMERG.
	
	0.1.4.3 - 4
		- Error correction.

0.1.5
	- Added the option to download half hourly Late and Early IMERG products.
	
	0.1.5.1 - 2 - 3
		- Error correction.
	
	0.1.5.4
		- Error correction, added IMERG download timeout of 15 seconds.
	
	0.1.5.5 - 6 - 7 - 8 - 9 - 10
		- Error correction.

0.1.6
	- Added Percentage Error function to FACETA.py and to all the distribution classes.
	- Change the distribution classes to not calculate the bias indexes until call with goodness_fit method.

0.1.7
	- Change the name of Precipitation_Analysis to Rainfall_Indices and changed its funcionalities.

0.1.8
	- Change the name of Precipitation_test to Statictical_Tests and changed its funcionalities.

	0.1.8.1 - 2
		- Error correction.

0.1.9
	- Updated search_loc function.
	
	0.1.9.1 - 2 - 3
		- Error correction.

0.1.10
	- Updated Rainfall_Indices class.
	- Created the Rain_Gauge class in hidro_tools.py.
	- Updated index from README.md.
	
	0.1.10.1
		- Error correction.

0.1.11
	- Updated Rain_Gauge class.

0.2.0
	- Change name of standard_error method in FACETA.py to root_mean_squared_error
	
	0.2.0.1
		- Error correction.

0.2.1
	- Changed how text in Savemap works

0.2.2
	- Added IDW_Grid_Interpolation class to geo_tools.py

0.2.3
	- Try to use second max for outliers:
		- Added sorted_max to Rainfall_Indices in hidro_tools.py
	
	0.2.3.1 - 2 - 3 - 4 - 5
		- Error correction.

0.3.0
	- Added more description and changed how to install and import libraries
	
	0.3.0.1
		- Error correction.
	
	0.3.0.2 - 3 - 4
		- Error correction. Changed, it was saving initial time of IMERG data, it should be the end time.

0.3.1
	- Outliers Test has been change as it is describe in its documentation.
	
	0.3.1.1
		- Error correction.
	
	0.3.1.2 - 3 - 4 - 5
		- Added limits return from Outliers Test.

0.3.2
	- Changed how Rainfall_Indices works.
	
	0.3.2.1 - 2
		- Error correction.
	
	0.3.2.3
		- IDW_Grid_Interpolation, changed condition when distance is cero to a condition that applies when distances is less than a limit.

	0.3.2.4 - 5 - 6 - 7 - 8
		- Error correction.

0.3.3
	- Changed results format in Statictical_Tests.

0.3.4
	- Added earth_data_path system, where global data is located, like topography for etopo function.

0.3.5
	- Added Wald-Wolfowitz test and changed the current test to WW runs test.

0.4.0
	- Added download module.

	0.4.0.1
		- Error correction.

0.4.1
	- Changed FACETA module name to frequency_analysis.

0.4.2
	- Changed system of tests result, added a dictionary.

	0.4.2.1
		- Error correction.

0.4.3
	- Added new indice to Rainfall_Indices: firstHday, in which day of the period the value is higher than H.

0.5.0
	- Added Map class, a basemap.
	- Deleted Savemap class, moved to trash classes.

0.5.1
	- Added inside_bbox function to geo_tools.py.

0.5.2
	- Adapted homogeneity_pettitt for multidimensional arrays.

	0.5.2.1
		- Error correction.

0.6.0
	- Added Mann-Whitney homogeneity test and Wilcoxon test was modified.

	0.6.0.1
		- Error correction.

0.6.1
	- Added sorted_max to Rainfall_Indices.

0.6.2
	- Adapted outliers_bulletin17b for replacing outlier with second higher value of that year.

	0.6.2.1 - 2 - 3
		- Error correction.

0.6.3
	- Added a Card class to create plots and tables with information of a station.

	0.6.3.1
		- Error correction.

	0.6.3.2
		- Modified.

	0.6.3.3 - 4
		- Error correction.

	0.6.3.5 - 6 - 7
		- Modified.

0.6.4
	- Added Kolmogorov-Smirnov test for goodness of fit for distribution functions.

0.6.5
	- Added Card_IMERG.
	- Change results from Statictical_Tests.

0.6.6
	- Removed Anderson tests.

	0.6.6.1 - 2
		- Error correction.

	0.6.3.3
		- Modified.

	0.6.6.4 - 5 - 6 - 7
		- Error correction.

0.6.7
	- Added cut function to geo_tools.

	0.6.7.1 - 2
		- Error correction.

0.6.8
	- Added along axis application to sorted_max_calc in Rainfall_Indices.

	0.6.8.1
		- Modified.

	0.6.8.2 - 3 - 4
		- Modified cut function.

	0.6.8.5
		- Error correction.

0.7.0
	- Changed how to detect start_month from the hydrological year
	- Changed name of detect_wet_period method from Rain_Gauge to detect_start_month.
	- Added adjacent_months function to hidro_tools module.

0.8.0
	- Added a new module, rg_pre.py, for preprocessing rain gauge data.

	0.8.0.1 - 2 - 3 - 4 - 5 - 6 - 7
		- Error correction.

0.8.1
	- Added functions to geo_tools.py:
		- get_imerg_analysis
		- get_imerg_idw
		- get_imerg_daily_sum
		- get_imerg_dataset
	- Added functions to frequency_analysis.py:
		- frequency_analysis
		- freq_conditions
	- Added tools.py module with function bin_file.

	0.8.1.1
		- Modified.

	0.8.1.2 - 3 - 4 - 5
		- Error correction.

0.8.2
	- Added master_results.py module with functions:
		- map_start_month
		- map_station_institution
		- map_station_test

	0.8.2.1
		- Modified.

0.8.3
	- Added the function map_error to master_result.py.

0.8.4
	- Added functions to geo_tools.py.

	0.8.4.1 - 2
		- Modified.

	0.8.4.3
		- Error correction.

	0.8.4.4 - 5
		- Modified.

0.8.5
	- Modified IDW_Grid_Interpolation.

	0.8.5.1 - 2 - 3
		- Modified.

0.8.6
	- Added interpolation_method_comparison to master_results.py.

0.8.7
	- Added RegularGridInterpolator to geo_tools.py.
	- Modified root_mean_squared_error to use sklearn.

	0.8.7.1 - 2 - 3
		- Modified.

	0.8.7.4 - 5 - 6
		- Error correction.

0.8.8
	- Added some functions to master_results.py.

0.8.9
	- Added a function to master_results.py.

	0.8.9.1 - 2 - 3 - 4 - 5 - 6 - 7 - 8 - 9 - 10 - 11 - 12
		- Modified.

0.8.10
	- Added a function to master_results.py.

	0.8.10.1 - 2 - 3
		- Modified.

0.8.11
	- Added a function to master_results.py.

	0.8.11.1
		- Modified.

0.9.0
	- Name of the library changed to PydroDesign.
	- Name of the module changed to RiSA (Rainfall Statistical Analysis).

# Index

rainfall