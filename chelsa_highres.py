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

# *************************************************
# import functions and modules
# *************************************************

import os as os
from functions.ingester import *
from functions.saga_functions import *
from functions.chelsa_functions import *
from functions.chelsa_data_classes import *
from functions.helper.set_ncdf_attributes import set_ncdf_attributes

# *************************************************
# global parameters
# *************************************************

debugging = False

if (debugging == True):
    TEMP='/home/karger/scratch/'
    INPUT='/storage/karger/chelsa_V2/INPUT_HIGHRES/'
    OUTPUT='/storage/karger/chelsa_V2/OUTPUT_HIGHRES/'
    YEAR=2012
    MONTH=2
    DAY=2
    HOUR=12

process = psutil.Process(os.getpid())
saga_api.SG_Set_History_Depth(0)

# *************************************************
# Get the command line arguments
# *************************************************

ap = argparse.ArgumentParser(
    description='''# This python code for CHELSA_V2.1_HIGHRES
is adapted to the ERA5 data. It runs the CHELSA algorithm for 
air temperature (tas), total downwelling shortwave solar radiation (rsds), total downwelling longwave 
solar radiation (rlsd), near-surface air pressure (ps), near-surface (10m) wind speed (sfcWind), near-surface
relative humidity (hurs), surface cloud area fraction (clt), near-surface air temperature lapse rates (tz), and total surface precipitation rate (pr). 
The output directory needs the following 
subfolders: /rsds, /rlds, /ps, /hurs/, /pr, /tas, /clt, /tz, /sfcWind.
Dependencies for ubuntu_18.04:
libwxgtk3.0-dev libtiff5-dev libgdal-dev libproj-dev 
libexpat-dev wx-common libogdi3.2-dev unixodbc-dev
g++ libpcre3 libpcre3-dev wget swig-4.0.1 python2.7-dev 
software-properties-common gdal-bin python-gdal 
python2.7-gdal libnetcdf-dev libgdal-dev
python-pip cdsapi saga_gis-8.2.0 cdo nco 
All dependencies are resolved in the chelsa_highres_V.1.0.sif singularity container
Tested with: singularity version 3.3.0-809.g78ec427cc
''',
    epilog='''author: Dirk N. Karger, dirk.karger@wsl.ch, Version 1.0'''
)

# collect the function arguments
ap.add_argument('-y','--year', type=int, help="year, integer")
ap.add_argument('-m','--month', type=int, help="month, integer")
ap.add_argument('-d','--day', type=int,  help="day, integer")
ap.add_argument('-hr','--hour', type=int, help='hour, integer')
ap.add_argument('-i','--input', type=str, help="input directory, string")
ap.add_argument('-o','--output', type=str,  help="output directory, string")
ap.add_argument('-t','--temp', type=str, help="root for temporary directory, string")
ap.add_argument('-er','--era5', type=str, help="directory for storing era5 input files, string")
ap.add_argument('-u','--username', type=str, help="username for mistral@dkrz.de, string")
ap.add_argument('-p','--password', type=str, help="password for mistral@dkrz.de, string")

args = ap.parse_args()
print(args)

# *************************************************
# Get arguments
# *************************************************

YEAR = args.year
DAY = args.day
MONTH = args.month
HOUR = args.hour

# *************************************************
# Set the directories from arguments
# *************************************************

INPUT = args.input
OUTPUT = args.output
TEMP = args.temp
ERA5store = args.era5
username = args.username
password = args.password

TEMP = str(TEMP + str(YEAR) + str("%02d" % MONTH) + str("%02d" % DAY) + str("%02d" % HOUR) + '/')

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
                  ERA5store=ERA5store,
                  hour=HOUR,
                  username=username,
                  password=password)

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

    pr = grid_calculator_simple(pr, 'a*1000*1000') # mm/1000/1h
    pr.Save(TEMP + 'pr_high.sgrd')

    #ps = grid_calculator_simple(ps, 'a*0.1') # hPa/10  CHECK !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ps.Save(TEMP + 'ps_high.sgrd')

    tcc = grid_calculator_simple(tcc, 'a*100') # fraction
    tcc.Save(TEMP + 'tcc_high.sgrd')

    hurs = grid_calculator_simple(hurs, 'a*10000') # %/100
    hurs.Save(TEMP + 'hurs_high.sgrd')

    #rsds = grid_calculator_simple(rsds, 'a*10') # kJ/s/m2
    rsds.Save(TEMP + 'rsds_high.sgrd')

    rlds = grid_calculator_simple(rlds, 'a*0.1') # (W/10)/m2
    rlds.Save(TEMP + 'rlds_high.sgrd')

    wind_speed = grid_calculator_simple(wind_speed, 'a*100') # (m/100)/s
    wind_speed.Save(TEMP + 'sfcWind_high.sgrd')

    ### convert files to ncdf
    outfile = OUTPUT + 'tas/CHELSA_HR_tas_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'tas_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='tas',
                        scale='0.1',
                        offset='0',
                        standard_name='air_temperature',
                        longname='Near-Surface Air Temperatures',
                        unit='K')

    outfile = OUTPUT + 'pr/CHELSA_HR_pr_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'pr_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='pr',
                        scale='0.001',
                        offset='0',
                        standard_name='precipitation_flux',
                        longname='Precipitation',
                        unit='kg m-2 h-1')

    outfile = OUTPUT + 'ps/CHELSA_HR_ps_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'ps_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='ps',
                        scale='10',
                        offset='0',
                        standard_name='surface_air_pressure',
                        longname='Surface Air Pressure',
                        unit='Pascal')

    outfile = OUTPUT + 'clt/CHELSA_HR_clt_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'tcc_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='clt',
                        scale='0.01',
                        offset='0',
                        standard_name='cloud_area_fraction',
                        longname='Cloud Area Fraction',
                        unit='Fraction')

    outfile = OUTPUT + 'hurs/CHELSA_HR_hurs_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'hurs_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='hurs',
                        scale='0.01',
                        offset='0',
                        standard_name='relative_humidity',
                        longname='Near-Surface Relative Humidity',
                        unit='%')

    outfile = OUTPUT + 'rsds/CHELSA_HR_rsds_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'rsds_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='rsds',
                        scale='1',
                        offset='0',
                        standard_name='surface_downwelling_shortwave_flux_in_air',
                        longname='Surface Downwelling Shortwave Radiation',
                        unit='kJ m-2')

    outfile = OUTPUT + 'rlds/CHELSA_HR_rlds_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'rlds_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='rlds',
                        scale='1',
                        offset='0',
                        standard_name='surface_downwelling_longwave_flux_in_air',
                        longname='Surface Downwelling Longwave Radiation',
                        unit='W m-2')

    outfile = OUTPUT + 'sfcWind/CHELSA_HR_sfcWind_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'sfcWind_high.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='sfcWind',
                        scale='0.01',
                        offset='0',
                        standard_name='wind_speed',
                        longname='Near-Surface Wind Speed',
                        unit='m s-1')

    outfile = OUTPUT + 'tz/CHELSA_HR_tz_' + str(YEAR) + '-' + str("%02d" % MONTH) + '-' + str("%02d" % DAY) + '-' + str("%02d" % HOUR) + '_V.1.0.nc'
    os.system('gdal_translate -ot Float32 -co "COMPRESS=DEFLATE" -co "ZLEVEL=9" ' + TEMP + 'tz.sdat ' + outfile)
    set_ncdf_attributes(outfile=outfile,
                        var='tz',
                        scale='1',
                        offset='0',
                        standard_name='temperature_lapse_rate',
                        longname='Near-Surface Temperature Lapse Rate in Air',
                        unit='K m-1')

    
    shutil.rmtree(TEMP)

if __name__ == '__main__':
    main()










