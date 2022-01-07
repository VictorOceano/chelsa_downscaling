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
#along with chelsa_cmip6.  If not, see <https://www.gnu.org/licenses/>.

import cdsapi
from getpass import getpass
import os as os
import xarray as xr

# set the username and password for access to mistral.dkrz.de
mistral_password = getpass('Mistral Password')
mistral_username = getpass('Mistral Username') #'b381089'

def get_era_via_mistral(parameter, type, year, month,  outdir, path='/pool/data/ERA5', mistral_username=None, mistral_password=None, day=False, ):
    if day==False:
        filename = path + '/' + type + '/' + year + '/E5' + type + '_' + year + '-' + month + '_' + parameter
    else:
        filename = path + '/' + type + '/' + year + '/E5' + type + '_' + year + '-' + month + '-' + day + '_' + parameter
    os.system('sshpass -p ' + mistral_password + ' scp -o StrictHostKeyChecking=no -r ' + mistral_username + '@mistral.dkrz.de:/' + filename + ' ' + outdir + 'tmp_' + parameter + '.grib')
    print ('file downloaded. Starting transformation ...')
    os.system('cdo -R remapcon,r1440x720 -setgridtype,regular ' + outdir + 'tmp_' + parameter + '.grib ' + outdir + 'tmp_' + parameter + '.nc')
    x1 = xr.open_dataset(outdir + 'tmp_' + parameter + '.nc', engine='cfgrib')
    x1.to_netcdf(outdir + parameter + '.nc')
    os.remove(outdir + 'tmp_' + parameter + '.nc')
    print ('done')

    return True


class get_era_via_api:
    """download era data class"""
    def __init__(self, year, month, day, hour, tmp):
        """ Create a set of baseline clims """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.tmp = tmp
        self.times = [
                    '00:00','01:00','02:00',
                    '03:00','04:00','05:00',
                    '06:00','07:00','08:00',
                    '09:00','10:00','11:00',
                    '12:00','13:00','14:00',
                    '15:00','16:00','17:00',
                    '18:00','19:00','20:00',
                    '21:00','22:00','23:00'
                ]
        self.plevels_temp = ['850', '950']
        self.c = cdsapi.Client()


    def albedo(self):
        self.c.retrieve(
        'reanalysis-era5-land',
        {
            'format': 'netcdf',
            'variable': 'forecast_albedo',
            'day': self.day,
            'time': self.times[int(self.hour)],
            'month': self.month,
            'year': self.year,
        },
        self.tmp + 'albedo_' + self.times[int(self.hour)] + '.nc')

        return True


    def tal1(self):
        self.c.retrieve(
        'reanalysis-era5-land',
        {
            'format': 'netcdf',
            'variable': 'soil_temperature_level1',
            'day': self.day,
            'time': times[int(self.hour)],
            'month': self.month,
            'year': self.year,
        },
        self.tmp + 'skintemp_' + self.times[int(self.hour)] +'.nc')

        return True

    
    def tal2(self):
        self.c.retrieve(
        'reanalysis-era5-land',
        {
            'format': 'netcdf',
            'variable': 'soil_temperature_level1',
            'day': self.day,
            'time': self.times[int(self.hour)],
            'month': self.month,
            'year': self.year,
        },
        self.tmp + 'skintemp_' + self.times[int(self.hour)] +'.nc')

        return True


    def lst(self):
        self.c.retrieve(
        'reanalysis-era5-land',
        {
            'format': 'netcdf',
            'variable': 'skin_temperature',
            'day': self.day,
            'time': self.times[int(self.hour)],
            'month': self.month,
            'year': self.year,
        },
        self.tmp + 'skintemp_' + self.times[int(self.hour)] +'.nc')

        return True


