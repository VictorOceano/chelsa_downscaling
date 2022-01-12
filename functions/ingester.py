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

import xarray as xr
import datetime
from helper.get_era5 import get_era5

def get_inputdata(year, month, day, TEMP, hour=None):
    # get uwind
    get_era5(parameter='165',
             type='sf00_1H',
             year=str(year),
             month=str("%02d" % month),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '165' + '_' + str(year) + '-' + str("%02d" % month) + '.nc')
    if hour:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')

    x1.to_netcdf(TEMP + 'u.nc')

    # get vwind
    get_era5(parameter='166',
             type='sf00_1H',
             year=str(year),
             month=str("%02d" % month),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '165' + '_' + str(year) + '-' + str("%02d" % month) + '.nc')
    if hour:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')

    x1.to_netcdf(TEMP + 'v.nc')


    # get tz
    get_era5(parameter='130',
             type='pl00_1H',
             year=str(year),
             month=str("%02d" % month),
             outdir=TEMP,
             path='/pool/data/ERA5',
             day=str("%02d" % day))
    x1 = xr.open_dataset(TEMP + '130' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    x1 = x1.loc[dict(isobaricInhPa=slice('950', '850'))]
    x1 = x1.drop(925, dim='isobaricInhPa')
    x1 = x1.drop(900, dim='isobaricInhPa')
    x1 = x1.drop(875, dim='isobaricInhPa')
    if hour:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 't.nc')

    # get geopotential height
    get_era5(parameter='129',
             type='pl00_1H',
             year=str(year),
             month=str("%02d" % month),
             day=str("%02d" % day),
             outdir=TEMP,
             path='/pool/data/ERA5')
    x1 = xr.open_dataset(TEMP + '129' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    x1 = x1.loc[dict(isobaricInhPa=slice('950', '850'))]
    x1 = x1.drop(925, dim='isobaricInhPa')
    x1 = x1.drop(900, dim='isobaricInhPa')
    x1 = x1.drop(875, dim='isobaricInhPa')
    if hour:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'z.nc')

    x1 = xr.open_dataset(TEMP + '129' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    if hour:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'zg.nc')

    # get tas
    get_era5(parameter='167',
             type='sf00_1H',
             year=str(year),
             month=str("%02d" % month),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '167' + '_' + str(year) + '-' + str("%02d" % month) + '.nc')
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')

    x1.to_netcdf(TEMP + 'tas_.nc')


    # get ps
    get_era5(parameter='134',
             type='sf00_1H',
             year=str(year),
             month=str("%02d" % month),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '134' + '_' + str(year) + '-' + str("%02d" % month) + '.nc')
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')

    x1.to_netcdf(TEMP + 'ps.nc')


    # get tcc
    get_era5(parameter='164',
             type='sf00_1H',
             year=str(year),
             month=str("%02d" % month),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '164' + '_' + str(year) + '-' + str("%02d" % month) + '.nc')
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')

    x1.to_netcdf(TEMP + 'tcc.nc')


    # get hurs
    get_era5(parameter='157',
             type='pl00_1H',
             year=str(year),
             month=str("%02d" % month),
             day=str("%02d" % day),
             outdir=TEMP,
             path='/pool/data/ERA5')
    x1 = xr.open_dataset(TEMP + '157' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    x1 = x1.sel(isobaricInhPa=1000)
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'hurs.nc')

    x1 = xr.open_dataset(TEMP + '157' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'rh.nc')

    # get cc
    get_era5(parameter='248',
             type='pl00_1H',
             year=str(year),
             month=str("%02d" % month),
             day=str("%02d" % day),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '248' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'cc.nc')


    # get uz ***********************************************************************************************************
    get_era5(parameter='131',
             type='pl00_1H',
             year=str(year),
             month=str("%02d" % month),
             day=str("%02d" % day),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '131' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'uz.nc')


    # get vz ***********************************************************************************************************
    get_era5(parameter='132',
             type='pl00_1H',
             year=str(year),
             month=str("%02d" % month),
             day=str("%02d" % day),
             outdir=TEMP,
             path='/pool/data/ERA5')

    x1 = xr.open_dataset(TEMP + '132' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')
    if hour:
        x1 = x1.sel(
            time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + 'T' + str("%02d" % hour) + str(
                ':00:00'))
    else:
        x1 = x1.sel(time=str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day))
        x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'vz.nc')

    # get pr ***********************************************************************************************************
    get_era5(parameter='228',
             type='sf12_01',
             year=str(year),
             month=str("%02d" % month),
             day=str("%02d" % day),
             outdir=TEMP,
             path='/pool/data/ERA5',
             hour=hour)

    year1 = year
    month1 = month
    if (day == 1 and hour < 6):
        if (month == 1):
            month1 = 12
            year1 = year - 1
        else:
            month1 = month - 1

    x1 = xr.open_dataset(TEMP + '228' + '_' + str(year1) + '-' + str("%02d" % month1) + '.nc')

    date_var = datetime.datetime(year, month, day)
    date_sel = date_var
    if (hour < 6):
        date_sel = date_var - datetime.timedelta(days=1)

    date_sel.strftime('%Y-%m:%d')
    print(date_sel)

    hours_ref_18 = [19,20, 21, 22, 23, 0, 1, 2, 3, 4, 5]
    hours_ref_06 = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

    x2 = None
    step = None
    if (hour in hours_ref_06):
        x1 = x1.sel(time=str(date_sel.year) + '-' + str("%02d" % date_sel.month) + '-' + str("%02d" % date_sel.day) + 'T06:00:00')
        step = hours_ref_06.index(hour) + 1
        x2 = x1.sel(step=str("%02d" % step) + ':00:00')

    if (hour in hours_ref_18):
        x1 = x1.sel(time=str(date_sel.year) + '-' + str("%02d" % date_sel.month) + '-' + str("%02d" % date_sel.day) + 'T18:00:00')
        step = hours_ref_18.index(hour) + 1
        x2 = x1.sel(step=str("%02d" % step) + ':00:00')

    if (hour == 6):
        x2 = x1.sel(time=str(date_sel.year) + '-' + str("%02d" % date_sel.month) + '-' + str(
            "%02d" % date_sel.day) + 'T06:00:00')

    if (hour == 18):
        x2 = x1.sel(time=str(date_sel.year) + '-' + str("%02d" % date_sel.month) + '-' + str(
            "%02d" % date_sel.day) + 'T18:00:00')

    x2.to_netcdf(TEMP + 'pr_.nc')























