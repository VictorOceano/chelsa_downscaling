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
