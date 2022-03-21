chelsa_highres
-----------
This package contains functions to creates hourly, or daily high-resolution 
climatologies for near-surface (2m) air temperature (tas), precipitation rate,
surface pressure (ps), surface relative humidity (hurs), 10m wind speed (sfcWind),
downwelling longwave solar radiation (rsds), downwelling longwave solar radiation (rlds),
atmospheric temperature lapse rates (tz), and total cloud cover fraction (clt). 
The code requires input from ERA5. Currently, it downloads the input data from the Mistral
cluster at DKRZ. To access the input data a username and password for Mistral is needed.
The code is part of the CHELSA Project: (CHELSA, <https://www.chelsa-climate.org/>).



COPYRIGHT
---------
(C) 2022 Dirk Nikolaus Karger



LICENSE
-------
chelsa_highres is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

chelsa_cmip6 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with chelsa_highres. If not, see <http://www.gnu.org/licenses/>.



REQUIREMENTS
------------
chelsa_highres is written in Python 2.7. 
All dependencies are resolved in the singularity container.
- python 2.7
- xarray 0.16.2
- datetime 3.9.2
- saga_api 8.1 (SAGA GIS compiled with --python-enabled)
- saga_api
- sys 2.7.15+
- argparse 1.1
- psutil 5.6.7



SINGULARITY
------------
All dependencies are also resolved in the singularity container 'chelsa_highres_V.1.0.sif'. Singularity needs to be installed on the respective linux system you are using. 
An installation guide can be found here: https://sylabs.io/guides/3.3/user-guide/quick_start.html#quick-installation-steps



INPUT DATA
------------
chelsa_highres is a mechanistic downscaling using topographic information. Therefore several orography grids need to be supplied. The resolution can vary, but the filenames should not be changed. The files need to be provided in a SAGA GIS grid format (.sgrd). The following input grids need to be provided:

orography:      This grid should contain the orography of the forcing data (e.g. ERA5)
dem_latlong:    This grid is the orography at the target resolution to which the climate data should be downscaled. It should be in a WGS84 geographic projection. The resolution is variable. but should be smaller than the resolution of the forcing data. The code has not been tested with resolutions larger then those of the dem_latlong3 grid.
dem_latlong3:   This grid is the resolution at which orographic cloud cover and windward leeward effects are modelled. The resolution should be around 3km.
dem_merc3:      The same as dem_latlong3 in a global mercator projection. PROJ4 string = +proj=merc +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs
dem_merc:       The same as dem_latlong in a gloabl mercator projection. PROJ4 string = +proj=merc +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs
expocor:        The expocor grid gives a correction for high elevation valleys. It needs to be calculated using SAGA GIS with the 'Wind Exposition Index' tool based on the dem_merc grid using the default values in SAGA GIS. Values above 1 should be set to 1 in the resulting grid H. The calculation of the final grid values E should be then done using: E = H*dem_latlong/9000. The resulting grid needs then to be reprojected to the same resolution and WGS84 projection of the dem_latlong grid.



HOW TO USE
----------
The chelsa_highres module provides all neccessary functions to downscale the respective climate parameters to a higher resolution.
The chelsa_data_classes.py provides the input data in form of pyhton classes.
The chelsa_functions.py contains the downscaling scripts
The saga_functions.py provides the api access functions to the saga_cmd functions written in C++
The ingester function loads the input data and does the neccessary transformations. If you adapt the code to new input data this is where you want to start.
The helper directory contains functions to download input data and to transform the output files. 



