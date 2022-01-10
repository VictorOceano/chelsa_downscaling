import saga_api, sys, os, argparse, datetime, os.path, cdsapi, psutil, shutil, gdal, subprocess
import xarray as xr
import cfgrib

use_mistral = True

def get_era5(parameter, type, year, month, outdir, path='/pool/data/ERA5', day=None):
    if day:
        outfile = outdir + parameter + '_' + year + '-' + month + '-' + day + '.nc'
    else:
        outfile = outdir + parameter + '_' + year + '-' + month + '.nc'

    if os.path.isfile(outfile):
        print ('nothing to do. file already exists')
    else:
        if day:
            filename = path + '/' + type + '/' + year + '/E5' + type + '_' + year + '-' + month + '-' + day + '_' + parameter
        else:
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
























