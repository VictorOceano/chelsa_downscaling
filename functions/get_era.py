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

# set times of the day and levels
times  = [
            '00:00','01:00','02:00',
            '03:00','04:00','05:00',
            '06:00','07:00','08:00',
            '09:00','10:00','11:00',
            '12:00','13:00','14:00',
            '15:00','16:00','17:00',
            '18:00','19:00','20:00',
            '21:00','22:00','23:00'
        ]

plevels_temp = [
                '850','950'
            ]

c = cdsapi.Client()

class get_era:
"""Interpolation class"""
    def __init__(self, year, month, day, hour, tmp):
        """ Create a set of baseline clims """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.tmp = tmp

    # tmean
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable':'2m_temperature',
            'year':self.year,
            'month':self.month,
            'day':self.day,
            'time':times[int(self.hour)],
            'format':'netcdf'
        },
        self.tmp + 'tmean.nc')

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': 'total_cloud_cover',
            'year':self.year,
            'month':self.month,
            'day':self.day,
            'time':times[int(self.hour)],
        },
        self.tmp + 'tcc.nc')

    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type':'reanalysis',
            'variable': 'geopotential',
            'pressure_level':plevels_temp,
            'year':self.year,
            'month':self.month,
            'day':self.day,
            'time': times[int(self.hour)],
            'format':'netcdf'
        },
        self.tmp + 'z_levels_'+times[int(self.hour)]+'.nc')

    # atmospheric temperature
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type':'reanalysis',
            'variable':
            'temperature'
            ,
            'pressure_level':plevels_temp,
            'year':self.year,
            'month':self.month,
            'day':self.day,
            'time': times[int(self.hour)],
            'format':'netcdf'
        },
        self.tmp + 't_levels_'+times[int(self.hour)]+'.nc')

    # albedo
    c.retrieve(
        'reanalysis-era5-land',
        {
            'format': 'netcdf',
            'variable': 'forecast_albedo',
            'day': self.day,
            'time': times[int(self.hour)],
            'month': self.month,
            'year': self.year,
        },
        self.tmp + 'albedo_'+times[int(self.hour)]+'.nc')


    # skin temperature
    c.retrieve(
        'reanalysis-era5-land',
        {
            'format': 'netcdf',
            'variable': 'skin_temperature',
            'day': self.day,
            'time': times[int(self.hour)],
            'month': self.month,
            'year': self.year,
        },
        self.tmp + 'skintemp_'+times[int(self.hour)]+'.nc')


