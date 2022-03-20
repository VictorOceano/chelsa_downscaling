#!/usr/bin/env python

#This file is part of chelsa_isimip3b_ba_1km.
#
#chelsa_isimip3b_ba_1km is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_isimip3b_ba_1km is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with chelsa_isimip3b_ba_1km.  If not, see <https://www.gnu.org/licenses/>.

# ***************************************
# import libraries
# ***************************************

import saga_api
import sys
import os
import argparse
import datetime
import os.path
import cdsapi
import psutil
import shutil
import xarray as xr

# *************************************************
# import functions and classes
# *************************************************

from functions.ingester import *
from functions.saga_functions import *
from functions.chelsa_functions import *
from functions.chelsa_data_classes import *

# *************************************************
# global parameters
# *************************************************

TEMP='/home/karger/scratch/'
ERA5store='/storage/karger/ERA5/store/'
INPUT='/storage/karger/chelsa_V2/INPUT_HIGHRES/'
YEAR=2002
MONTH=1
DAY=3
HOUR=0
year=2002
month=1
day=3
hour=0
username=''
password=''

process = psutil.Process(os.getpid())
saga_api.SG_Set_History_Depth(0)


#get_inputdata(year=YEAR,
#              month=MONTH,
#              day=DAY,
#              TEMP=TEMP,
#              ERA5store=ERA5store,
#              hour=HOUR)


### create the data classes
coarse_data = Coarse_data(TEMP=TEMP)
dem_data = Dem_data(INPUT=INPUT)
aux_data = Aux_data(INPUT=INPUT)

tcc = load_sagadata('/home/karger/scratch/tcc_high.sgrd')
# shortwave solar radiation downwards

Dem = dem_data



csr = solar_radiation(cc=tcc,
                            Dem=dem_data,
                            year=YEAR,
                            month=MONTH,
                            day=DAY,
                            hour=HOUR)













coarse_data.set('tlapse_mean')

coarse_data.tlapse_mean.Save(TEMP + 'tlapse.sgrd')

tas = temperature(Coarse=coarse_data,
                  Dem=dem_data,
                  var='tas')

tas.Save(TEMP + 'tas_high.sgrd')

ps_high = surface_pressure(Coarse=coarse_data,
                           Dem=dem_data)

ps_high.Save(TEMP + 'ps_high.sgrd')

windef = calculate_windeffect(Coarse=coarse_data, Dem=dem_data)

wind_cor, wind_coarse = correct_windeffect(windef1=windef,
                                           Coarse=coarse_data,
                                           Aux=aux_data,
                                           Dem=dem_data)

wind_cor.Save(TEMP + 'wind_cor.sgrd')


tcc = cloud_cover(Coarse=coarse_data, Dem=dem_data, windeffect=wind_cor)

tcc.Save(TEMP + 'tcc_high.sgrd')

rsds, csr = solar_radiation(tcc,
                            Dem=dem_data,
                            year=YEAR,
                            month=MONTH,
                            day=DAY,
                            hour=HOUR)

rsds.Save(TEMP + 'rsds.sgrd')


hurs = relative_humidity(Coarse=coarse_data,
                         Dem=dem_data,
                         windeffect=wind_cor)

hurs.Save(TEMP + 'hurs_high.sgrd')

rlds = longwave_radiation_downwards(rsds=rsds,
                                   csr=csr,
                                   hurs=hurs,
                                   tas=tas)

rlds.Save(TEMP + 'rlds_high.sgrd')

pr = precipitation(wind_cor=wind_cor,
                   wind_coarse=wind_coarse,
                   Coarse=coarse_data)

pr.Save(TEMP + 'pr_high.sgrd')


wind_dir, wind_speed = wind_speed_direction(Coarse=coarse_data, Dem=dem_data)

wind_speed.Save(TEMP + 'windspeed_high.sgrd')
