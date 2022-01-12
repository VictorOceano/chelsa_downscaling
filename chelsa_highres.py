#!/usr/bin/env python

#This file is part of chelsa_highres.
#
#chelsa_isimip3b_ba_1km is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_highres is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with chelsa_cmip6.  If not, see <https://www.gnu.org/licenses/>.

from functions.ingester import *
from functions.saga_functions import *
from functions.chelsa_functions import *
from functions.chelsa_data_classes import *

# *************************************************
# global parameters
# *************************************************

TEMP='/home/karger/scratch/'
INPUT='/storage/karger/chelsa_V2/INPUT_HIGHRES/'
YEAR=2001
MONTH=1
DAY=1
HOUR=12

process = psutil.Process(os.getpid())
saga_api.SG_Set_History_Depth(0)



# *************************************************
# Get the command line arguments
# *************************************************
ap = argparse.ArgumentParser(
    description='''# This python code is adapted for CHELSA_V2.1_HIGHRES
the code is adapted to the ERA5 data. It runs the CHELSA algorithm for 
air temperature (tas), total downwelling shortwave solar radiation (rsds), total downwelling longwave 
solar radiation (rlsd), near-surface air pressure (ps), near-surface (10m) wind speed (sfcWind), near-surface
relative humidity (hurs), near-surface air temperature lapse rates (tz), and total surface precipitation rate (pr). 
The output directory needs the following 
subfolders: /rsds, /rlds, /ps, /hurs/, /pr, /tas, /tz, /sfcWind.
Dependencies for ubuntu_18.04:
libwxgtk3.0-dev libtiff5-dev libgdal-dev libproj-dev 
libexpat-dev wx-common libogdi3.2-dev unixodbc-dev
g++ libpcre3 libpcre3-dev wget swig-4.0.1 python2.7-dev 
software-properties-common gdal-bin python-gdal 
python2.7-gdal libnetcdf-dev libgdal-dev
python-pip cdsapi saga_gis-7.6.0
All dependencies are resolved in the chelsa_V2.1.cont singularity container
Tested with: singularity version 3.3.0-809.g78ec427cc
''',
    epilog='''author: Dirk N. Karger, dirk.karger@wsl.ch, Version 1.0'''
)

# collect the function arguments
ap.add_argument('-y','--year', type=int, help="year, integer")
ap.add_argument('-m','--month', type=int, help="month, integer")
ap.add_argument('-d','--day', type=int,  help="day, integer")
ap.add_argument('-h','--hour', type=int, help= 'hour, integer')
ap.add_argument('-i','--input', type=str, help="input directory, string")
ap.add_argument('-o','--output', type=str,  help="output directory, string")
ap.add_argument('-t','--temp', type=str, help="root for temporary directory, string")

args = ap.parse_args()
print(args)

# *************************************************
# Get arguments
# *************************************************

year = args.year
day = args.day
month = args.month
hour = args.hour

# *************************************************
# Set the directories from arguments
# *************************************************

INPUT = args.input
OUTPUT = args.output
TEMP = args.temp
TEMP = str(TEMP + year + month + day + hour + '/')

if os.path.exists(TEMP) and os.path.isdir(TEMP):
    shutil.rmtree(TEMP)

os.mkdir(TEMP)

# ************************************************
# Script
# ************************************************
def main():
    get_inputdata(year=YEAR,
                  month=MONTH,
                  day=DAY,
                  TEMP=TEMP,
                  hour=HOUR)

    ### create the data classes
    coarse_data = Coarse_data(TEMP=TEMP)
    dem_data = Dem_data(INPUT=INPUT)
    aux_data = Aux_data(INPUT=INPUT)
    coarse_data.set('tlapse_mean')

    ### downscale the variables

    # 2m air temperature
    tas = temperature(Coarse=coarse_data,
                      Dem=dem_data,
                      var='tas')

    # near-surface air-pressure
    ps = surface_pressure(Coarse=coarse_data,
                          Dem=dem_data)

    # windward-leeward index
    windef = calculate_windeffect(Coarse=coarse_data,
                                  Dem=dem_data)

    wind_cor, wind_coarse = correct_windeffect(windef1=windef,
                                               Coarse=coarse_data,
                                               Aux=aux_data,
                                               Dem=dem_data)
    # total cloud cover
    tcc = cloud_cover(Coarse=coarse_data,
                      Dem=dem_data,
                      windeffect=wind_cor)

    # shortwave solar radiation downwards
    rsds, csr = solar_radiation(tcc,
                                Dem=dem_data,
                                year=YEAR,
                                month=MONTH,
                                day=DAY,
                                hour=HOUR)

    # relative humidity
    hurs = relative_humidity(Coarse=coarse_data,
                             Dem=dem_data,
                             windeffect=wind_cor)

    # longwave radiation downwards
    rlds = longwave_radiation_downwards(rsds=rsds,
                                       csr=csr,
                                       hurs=hurs,
                                       tas=tas)

    # precipitation rate
    pr = precipitation(wind_cor=wind_cor,
                       wind_coarse=wind_coarse,
                       Coarse=coarse_data)

    # wind speed
    wind_dir, wind_speed = wind_speed_direction(Coarse=coarse_data,
                                                Dem=dem_data)

    ### scale and save the output variables
    tas = grid_calculator_simple(tas, 'a*10') # K/10
    tas.Save(TEMP + 'tas_high.sgrd')

    coarse_data.tlapse_mean.Save(TEMP + 'tz.sgrd') # K/m

    pr = grid_calculator_simple(tas, 'a*1000*1000') # mm/1000/1h
    pr.Save(TEMP + 'pr_high.sgrd')

    ps = grid_calculator_simple(ps, 'a*0.1') # hPa/10
    ps.Save(TEMP + 'ps_high.sgrd')

    tcc = grid_calculator_simple(tcc, 'a*1000') # %/10
    tcc.Save(TEMP + 'tcc_high.sgrd')

    hurs = grid_calculator_simple(hurs, 'a*1000') # %/10
    hurs.Save(TEMP + 'hurs_high.sgrd')

    rsds = grid_calculator_simple(rsds, 'a*10') # (kJ/10)/m2
    rsds.Save(TEMP + 'rsds_high.sgrd')

    rlds = grid_calculator_simple(rsds, 'a*0.01') # (kJ/10)/m2
    rlds.Save(TEMP + 'rlds_high.sgrd')

