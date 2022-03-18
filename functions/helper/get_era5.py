#!/usr/bin/env python

#This file is part of chelsa_highres.
#
#chelsa_highre is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_isimip3b_ba_1km is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with chelsa_highres.  If not, see <https://www.gnu.org/licenses/>.

import os as os
import xarray as xr
import time


def wait_until(outfile, timeout, period=1.0):
    mustend = time.time() + timeout
    while time.time() < mustend:
        accessright = os.access(outfile, os.R_OK)
        print('outfile: ' + outfile)
        print('accessright: ' + str(accessright))
        if accessright == True:
            print('access ok')
            return True
        time.sleep(period)
    return 'timeout: No file access.'


def get_era5(parameter, type, year, month, outdir, storedir, path='/pool/data/ERA5', day=None, hour=None):
    if (type == 'sf12_01'):
        # select the correct file. Forecast steps are starting 6:00 UTC and 18 UTC:
        if (day == '01' and hour < 6):
            if (month == '01'):
                month = '12'
                year = str(int(year) - 1)
            else:
                month = str(int(month) - 1)

    if day:
        outfile = storedir + parameter + '_' + year + '-' + month + '-' + day + '.nc'
        if (type == 'sf12_01'):
            outfile = storedir + parameter + '_' + year + '-' + month + '.nc'
    else:
        outfile = storedir + parameter + '_' + year + '-' + month + '.nc'

    if os.path.isfile(outfile):
        print ('no download needed. file already exists in filesystem. Checking file access ...')
        # check the file access
        wait_until(outfile, 300, 0.25)

    else:
        if day:
            filename = path + '/' + type + '/' + year + '/E5' + type + '_' + year + '-' + month + '-' + day + '_' + parameter
        else:
            filename = path + '/' + type + '/' + year + '/E5' + type + '_' + year + '-' + month + '_' + parameter
        if (type == 'sf12_01'):
            filename = path + '/' + type + '/' + year + '/E5' + type + '_' + year + '-' + month + '_' + parameter

        os.system(
            'sshpass -p 9331Joker1! scp -o StrictHostKeyChecking=no -r b381089@mistral.dkrz.de:/' + filename + ' ' + outdir + 'tmp_' + parameter + '.grib')
        print ('file downloaded. Starting transformation ...')
        os.system(
            'cdo -R remapcon,r1440x720 -setgridtype,regular ' + outdir + 'tmp_' + parameter + '.grib ' + outdir + 'tmp_' + parameter + '.nc')
        x1 = xr.open_dataset(outdir + 'tmp_' + parameter + '.nc', engine='cfgrib')

        x1.to_netcdf(outfile)
        os.remove(outdir + 'tmp_' + parameter + '.nc')
        os.remove(outdir + 'tmp_' + parameter + '.grib')
        print ('done')

    return True
