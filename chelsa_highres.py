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
#along with chelsa_cmip6.  If not, see <https://www.gnu.org/licenses/>.

from functions.saga_functions import *
from functions.get_era import *

year = 1982
month = 12
day = 30
hour = 11
tmp = '/home/karger/scratch/'

era_data = get_era_via_api(year=year,
                           month=month,
                           day=day,
                           hour=hour,
                           tmp=tmp)


era_data.albedo()
era_data.lst()
era_data.tal1()
era_data.tal2()

if __name__ == '__main__':
    saga_api.SG_Get_Data_Manager().Delete_All()  #

    Load_Tool_Libraries(True)


    ### calculate temprature lapserates *******************************************************

    filename = TEMP + 't_levels_' + times[int(hour)] + '.nc'
    tlevels  = import_ncdf(filename)
    filename = TEMP + 'z_levels_' + times[int(hour)] + '.nc'
    zlevels  = import_ncdf(filename)
    zlevels.Get_Grid(0).Set_Scaling(zlevels.Get_Grid(0).Get_Scaling() * 0.10197162129)
    zlevels.Get_Grid(1).Set_Scaling(zlevels.Get_Grid(1).Get_Scaling() * 0.10197162129)
    tz  = tlapse(zlevels.Get_Grid(0), zlevels.Get_Grid(1), tlevels.Get_Grid(0), tlevels.Get_Grid(1), '(d-c)/(b-a)')
    tz1 = change_latlong(tz)
    tz1.Get_Projection().Create(saga_api.CSG_String('+proj=longlat +datum=WGS84 +no_defs'), saga_api.SG_PROJ_FMT_Proj4)

    # get mean temperature
    tas = import_ncdf(TEMP + 'tmean.nc')
    tas1 = change_latlong(tas.Get_Grid(0))
    tas1.Get_Projection().Create(saga_api.CSG_String('+proj=longlat +datum=WGS84 +no_defs'), saga_api.SG_PROJ_FMT_Proj4)

    # reproject grids
    dem = import_gdal(INPUT + 'ArcticDEM_Disko_tile_merge_cropped_S.tif')
    dem_latlong = import_gdal(INPUT + 'ArcticDEM_Disko_tile_merge_cropped_S_latlong.tif')

    tas_pj = clip_grid(tas1,dem_latlong,3)
    tz_pj  = clip_grid(tz1,dem_latlong,3)

    tz_shp = gridvalues_to_points(tz_pj)
    tas_shp = gridvalues_to_points(tas_pj)

    ## reproject
    tz_shp = reproject_shape(tz_shp,dem)
    tas_shp = reproject_shape(tas_shp,dem)

    ## multilevel b spline
    tz_ras = triangulation(tz_shp,dem)
    tas_ras = triangulation(tas_shp,dem)

    rsds, ratio = srad(dem)

    # load the orography
    orog = load_sagadata(INPUT + 'orography.sgrd')
    orog = change_latlong(orog)
    orog.Get_Projection().Create(saga_api.CSG_String('+proj=longlat +datum=WGS84 +no_defs'), saga_api.SG_PROJ_FMT_Proj4)
    orog_pj = clip_grid(orog,dem_latlong,3)
    orog_shp = gridvalues_to_points(orog_pj)
    orog_shp = reproject_shape(orog_shp,dem)
    orog_ras = triangulation(orog_shp,dem)

    # load the cloudcover
    tcc = import_ncdf(TEMP + 'tcc.nc')
    tcc = change_latlong(tcc.Get_Grid(0))
    tcc.Get_Projection().Create(saga_api.CSG_String('+proj=longlat +datum=WGS84 +no_defs'), saga_api.SG_PROJ_FMT_Proj4)
    tcc_pj = clip_grid(tcc,dem_latlong,3)
    tcc_shp = gridvalues_to_points(tcc_pj)
    tcc_shp = reproject_shape(tcc_shp,dem)

    # downscale the temperatures
    tas_high = lapse_rate_based_downscaling(dem,tz_ras,orog_ras,tas_ras)
    tcc_ras = triangulation(tcc_shp,tas_high)
    tas_srad = temp_srad_cc_correction(tas_high,ratio,tcc_ras,'tas')

    # correct the solar radiation by cloud cover
    rsds_cl = grid_calculator(rsds, tcc_ras, 'a*(1.0-0.75*b^(3.4))' )
    # convert kWh/m**-2 to W/m**-2
    rsds_cl = grid_calculator(rsds_cl,rsds_cl,'a*0.1142')
    # read the albedo

    albedo = import_ncdf(TEMP + 'albedo_' + times[int(hour)] + '.nc')

    albedo = change_latlong(albedo.Get_Grid(0))

    albedo.Get_Projection().Create(saga_api.CSG_String('+proj=longlat +datum=WGS84 +no_defs'), saga_api.SG_PROJ_FMT_Proj4)

    albedo_pj = clip_grid(albedo, dem_latlong, 3)

    albedo_shp = gridvalues_to_points(albedo_pj)

    albedo_shp = reproject_shape(albedo_shp,
                                 dem)

    albedo_ras = multilevel_B_spline(albedo_shp,
                                     dem)

    tas_sky = grid_calculator(tas_high,
                              tas_high,
                              'a-20')

    lst = calc_LST(rsds_cl,
                   tas_high,
                   tas_sky,
                   albedo_ras)

    # save the outputs
    outfile2 = OUTPUT + 'tas/CHELSA_tas_' + times[int(hour)] + '_' + day + '_' + month + '_' + year + '.V.1.0.tif'
    export_geotiff(tas_high,outfile2)
    outfile2 = OUTPUT + 'lst/CHELSA_lst_' + times[int(hour)] + '_' + day + '_' + month + '_' + year + '.V.1.0.tif'
    export_geotiff(lst,outfile2)
    outfile2 = OUTPUT + 'tz/CHELSA_tz_' + times[int(hour)] + '_' + day + '_' + month + '_' + year + '.V.1.0.tif'
    export_geotiff(tz1,outfile2)
    outfile2 = OUTPUT + 'rsds/CHELSA_rsds_' + times[int(hour)] + '_' + day + '_' + month + '_' + year + '.V.1.0.tif'
    export_geotiff(rsds_cl,outfile2)
    outfile2 = OUTPUT + 'cssr/CHELSA_cssr_' + times[int(hour)] + '_' + day + '_' + month + '_' + year + '.V.1.0.tif'
    export_geotiff(rsds,outfile2)

    print(datetime.datetime.now())
    # remove the temporary directory
    shutil.rmtree(TEMP)

