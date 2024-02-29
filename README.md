![Portada_BG](https://github.com/joaquinseguraellis/PydroDesign/assets/57773288/153cdcb2-8e92-4641-bbe0-df5a2ab7a316)
# Introduction
This library has several tools for statistical analysis of rainfall series.  
The main purpose of this library is to compare IMERG rainfall with rain gauges and give the results of it.
# How to install
```
pip install --user --upgrade --force-reinstall "git+https://github.com/joaquinseguraellis/PydroDesign.git"
```
# Example
Here is an example of the results when comparing rain gauge with IMERG rainfall estimates:
```
from RiSA.results import get_design_rainfall

get_design_rainfall(
    product='Final', T=50, lon=-64.20, lat=-31.42,
)
```
The output is:
```
{
    'longitude': -64.2,
    'latitude': -31.42,
    'in Arg': True,
    'Return period': 50,
    'Lower limit': 103.2275530007228,
    'Estimate': 133.04581865484533,
    'Higher limit': 171.66438455465254,
}
```
# Citation

# Dependencies
Consejo Nacional de Investigaciones Científicas y Técnicas ([**CONICET**](https://www.conicet.gov.ar/))  
Facultad de Ciencias Exactas, Físicas y Naturales. Universidad Nacional de Córdoba ([**FCEFyN**](https://fcefyn.unc.edu.ar/))
