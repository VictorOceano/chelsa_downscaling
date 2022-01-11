import saga_api, sys, os, argparse, os.path, cdsapi, psutil, shutil, gdal, subprocess
import xarray as xr
import datetime

import cfgrib

use_mistral = True

def get_era5(parameter, type, year, month, outdir, path='/pool/data/ERA5', day=None, hour=None):
    if (type == 'sf12_01'):
        # select the correct file. Forecast steps are starting 6:00 UTC and 18 UTC:
        if (day == '01' and hour < 6):
            if (month == '01'):
                month = '12'
                year = str(int(year) - 1)
            else:
                month = str(int(month) - 1)

    if day:
        outfile = outdir + parameter + '_' + year + '-' + month + '-' + day + '.nc'
        if (type == 'sf12_01'):
            outfile = outdir + parameter + '_' + year + '-' + month + '.nc'
    else:
        outfile = outdir + parameter + '_' + year + '-' + month + '.nc'

    if os.path.isfile(outfile):
        print ('nothing to do. file already exists')
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


#2m temperature: 167

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

    step=None
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



def get_pr_locally(PREC, TEMP, year, month, day, hour=None):
    # get pr , this parameter is not on mistral, so it needs to be available locally
    if day:
        outfile = TEMP + '228_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc'

    os.system(
        'cdo -R remapcon,r1440x720 -setgridtype,regular ' + PREC + 'pr_' + str(year) + '-' + str("%02d" % month) + '-'
        + str("%02d" % day) + '.grib ' + TEMP + 'tmp_228.nc')
    x1 = xr.open_dataset(TEMP + 'tmp_228.nc', engine='cfgrib')
    x1.to_netcdf(outfile)

    x1 = xr.open_dataset(TEMP + '228' + '_' + str(year) + '-' + str("%02d" % month) + '-' + str("%02d" % day) + '.nc')

    if hour:
        x2 = x1.sel(step=str("%02d" % hour) + str(':00:00'))
    else:
        x2 = x1.mean(dim='step')

    x2.to_netcdf(TEMP + 'pr_.nc')

    return True






















