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
#along with isimip3b_ba_1km.  If not, see <https://www.gnu.org/licenses/>.


from functions.saga_functions import *
from functions.chelsa_data_classes import *
Load_Tool_Libraries(True)


def temperature(Coarse, Dem, var):
    # load coarse temperature data
    if var == 'tas':
        Coarse.set('tas_')
        temp_in = Coarse.tas_
    if var == 'tasmax':
        Coarse.set('tasmax')
        temp_in = Coarse.tasmax
    if var == 'tasmin':
        Coarse.set('tasmin')
        temp_in = Coarse.tasmin

    # do lapse-rate-based downscaling
    Coarse.set('tlapse_mean')
    Dem.set('dem_high')
    Dem.set('dem_low')
    temp_high = lapse_rate_based_downscaling(Dem.dem_high,
                                             Coarse.tlapse_mean,
                                             Dem.dem_low,
                                             temp_in)
    Coarse.delete('tlapse_mean')
    Dem.delete('dem_high')
    Dem.delete('dem_low')

    # multiply by 10 and cast to unsigned int
    temp_out = convert2uinteger10(temp_high, 'Daily Near-Surface Air Temperature')

    # clean memory
    saga_api.SG_Get_Data_Manager().Delete(temp_high)
    del temp_in

    return temp_out


def surface_pressure(Coarse, Dem):
    Coarse.set('tas_')
    Coarse.set('ps')
    Coarse.set('tlapse_mean')
    Dem.set('dem_high')
    Dem.set('dem_low')
    #Coarse.ps.Set_Scaling(0.01)

    ps_high = Air_Pressure(ps=Coarse.ps,
                           orog=Dem.dem_low,
                           tas=Coarse.tas_,
                           tz=Coarse.tlapse_mean,
                           dem_high=Dem.dem_high)

    return ps_high


def solar_radiation(Coarse, Dem, year, month, day, hour):
    # calculate solar radiation
    Dem.set('demproj')
    Dem.set('dem_high')

    csr = clear_sky_solar_radiation(dem_merc=Dem.demproj,
                                    year=year,
                                    month=month,
                                    day=day,
                                    hour=hour)

    csr_latlong = proj_2_latlong(csr, Dem.dem_high)

    Coarse.set('tcc')
    srad_sur = surface_radiation(csr_latlong,
                                 Coarse.tcc,
                                 'Surface Downwelling Shortwave Radiation')

    return srad_sur

