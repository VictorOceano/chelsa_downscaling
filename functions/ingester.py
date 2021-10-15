
if use_mistral==True:
    # get uwind
    get_era5(parameter='165',
             type='sf00_1H',
             year=str(year),
             month=str(month),
             outdir=TEMP,
             path='/pool/data/ERA5')
    x1 = xr.open_dataset(TEMP + '165.nc')
    x1 = x1.loc[dict(time=slice(str(year) + '-' + str(month) + '-' + str(day)))]
    x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'u.nc')
    # get vwind
    get_era5(parameter='166',
             type='sf00_1H',
             year=str(year),
             month=str(month),
             outdir=TEMP,
             path='/pool/data/ERA5')
    x1 = xr.open_dataset(TEMP + '166.nc')
    x1 = x1.loc[dict(time=slice(str(year) + '-' + str(month) + '-' + str(day)))]
    x1 = x1.mean(dim='time')
    x1.to_netcdf(TEMP + 'v.nc')
    #check if lapse rate exists
    if os.path.isfile(LAPSE + 'CHELSA_tz_' + day + '_' + month + '_' + year + '_V.2.1.tif')==False:
        # get temperature
        get_era5(parameter='130',
                 type='pl00_1H',
                 year=str(year),
                 month=str(month),
                 day=str(day),
                 outdir=TEMP,
                 path='/pool/data/ERA5')
        x1 = xr.open_dataset(TEMP + '130.nc')
        x1 = x1.loc[dict(isobaricInhPa=slice('950','850'))]
        x1 = x1.drop(925, dim='isobaricInhPa')
        x1 = x1.drop(900, dim='isobaricInhPa')
        x1 = x1.drop(875, dim='isobaricInhPa')
        x1 = x1.mean(dim='time')
        x1.to_netcdf(TEMP + 't.nc')
        # get geopotential height
        get_era5(parameter='129',
                 type='pl00_1H',
                 year=str(year),
                 month=str(month),
                 day=str(day),
                 outdir=TEMP,
                 path='/pool/data/ERA5')
        x1 = xr.open_dataset(TEMP + '129.nc')
        x1 = x1.loc[dict(isobaricInhPa=slice('950','850'))]
        x1 = x1.drop(925, dim='isobaricInhPa')
        x1 = x1.drop(900, dim='isobaricInhPa')
        x1 = x1.drop(875, dim='isobaricInhPa')
        x1 = x1.mean(dim='time')
        x1.to_netcdf(TEMP + 'z.nc')

#        tas = xr.open_dataset(TEMP + 't.nc')
#        zg = xr.open_dataset(TEMP + 'z.nc')


