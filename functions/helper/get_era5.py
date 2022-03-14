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
import hashlib
import requests


def wait_until(somepredicate, timeout, period=0.25, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if somepredicate(*args, **kwargs):
            return True
        time.sleep(period)
    return False


def md5Checksum(filePath,url):
    if url==None:
        with open(filePath, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()
    else:
        r = requests.get(url, stream=True)
        m = hashlib.md5()
        for line in r.iter_lines():
            m.update(line)
        return m.hexdigest()


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
        print ('no download needed. file already exists in filesystem. Checking md5 checksum...')
        md5_remote = os.popen('sshpass -p 9331Joker1! ssh -o StrictHostKeyChecking=no b381089@mistral.dkrz.de md5sum /home/b/b381089/test.test').read()
        md5_remote = md5_remote.split(" ", 1)[0]
        md5_locale = hashlib.md5(open(outfile, 'rb').read()).hexdigest()
        wait_until(md5_locale == md5_remote)

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
