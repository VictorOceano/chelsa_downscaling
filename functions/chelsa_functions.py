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
    # this function calculates 2m air temperature based on atmospheric lapse rates
    # and a high resolution DEM
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
    # this function calculates surface pressure using the barometric equation
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


def calculate_windeffect(Coarse, Dem):
    ## import the wind files
    Coarse.set('u')
    Coarse.set('v')

    uwind = Coarse.u
    vwind = Coarse.v

    ## set coordinate reference system
    set_2_latlong(uwind)
    set_2_latlong(vwind)

    ## change to shapefile for projection
    uwind_shp = gridvalues_to_points(uwind)
    vwind_shp = gridvalues_to_points(vwind)

    #Coarse._delete_grid_list_('ua100000')
    #Coarse._delete_grid_list_('va100000')

    ## reproject to mercator projection
    uwind_shp = reproject_shape(uwind_shp)
    vwind_shp = reproject_shape(vwind_shp)

    Dem.set('demproj')
    ## multilevel b spline
    uwind_ras = multilevel_B_spline(uwind_shp,
                                    Dem.demproj, 14)

    vwind_ras = multilevel_B_spline(vwind_shp,
                                    Dem.demproj, 14)

    direction = polar_coords(uwind_ras,
                             vwind_ras)

    #dem = change_data_storage(Dem.dem_latlong3)

    windef = windeffect(direction,
                        Dem.demproj)

    Dem.set('dem_latlong3')
    windef1 = proj_2_latlong(windef,
                             Dem.dem_latlong3)
    Dem.delete('dem_latlong3')

    # clean up memory
    saga_api.SG_Get_Data_Manager().Delete(uwind_ras)
    saga_api.SG_Get_Data_Manager().Delete(vwind_ras)
    saga_api.SG_Get_Data_Manager().Delete(uwind_shp)
    saga_api.SG_Get_Data_Manager().Delete(vwind_shp)
    saga_api.SG_Get_Data_Manager().Delete(windef)
    #saga_api.SG_Get_Data_Manager().Delete(dem)

    return windef1


def correct_windeffect(windef1, Coarse, Dem, Aux):
    Coarse.set('tas_')
    Coarse.set('hurs')

    cblev = grid_calculator(Coarse.tas_,
                            Coarse.hurs,
                            '(20+((a-273.15)/5))*(100-b)')

    Coarse.delete('tas_')
    Coarse.delete('hurs')

    cblev = calc_geopotential(cblev)
    set_2_latlong(cblev)
    cblev_shp = gridvalues_to_points(cblev)

    #dem_geo = calc_geopotential(Dem.dem_low)

    Dem.set('dem_low')
    cblev_ras = multilevel_B_spline(cblev_shp,
                                    Dem.dem_low, 14)

    # correct wind effect by boundary layer height
    pblh = grid_calculatorX(Dem.dem_low,
                            cblev_ras,
                            'a+(b/9.80665)')

    Dem.delete('dem_low')
    Dem.set('dem_high')

    dist2bound = calc_dist2bound(Dem.dem_high,
                                 pblh)
    Dem.delete('dem_high')

    maxdist2bound = resample_up(dist2bound,
                                pblh, 7)

    maxdist2bound2 = invert_dist2bound(dist2bound,
                                       maxdist2bound)

    wind_cor = grid_calculatorX(maxdist2bound2,
                                windef1,
                                '(b/(1-a/9000))')


    #patchgrid = Aux.patch #load_sagadata(INPUT + 'patch.sgrd')

    #exp_index = Aux.expocor #load_sagadata(INPUT + 'expocor.sgrd')

    Aux.set('expocor')
    wind_cor = grid_calculatorX(Aux.expocor,
                                wind_cor,
                                'a*b')

    Aux.delete('expocor')
    #Aux.set('patch')

    #wind_cor = patching(wind_cor,
    #                    Aux.patch)

    #Aux.delete('patch')
    #Aux.set('dummy_W5E5')

    #wind_coarse = resample_up(wind_cor,
    #                          Aux.dummy_W5E5, 4)

    #closegaps(wind_coarse)

    # downscale precipitation and export
    wind_coarse25 = resample_up(wind_cor,
                                pblh, 4)

    #Aux.delete('dummy_W5E5')

    return wind_cor, wind_coarse25 #, wind_coarse


def cloud_cover(Coarse, Dem, windeffect):
    Coarse.set('tas_')
    Coarse.set('hurs')
    levels = range(0, 37)
    levels.reverse()
    cblev = grid_calculator(Coarse.tas_,
                            Coarse.hurs,
                            '(20+((a-273.15)/5))*(100-b)')

    Dem.set('dem_high')
    dem_geo = calc_geopotential(Dem.dem_high)
    cblev_res = resample(cblev, Dem.dem_high)

    Coarse.set('cc')
    Coarse.set('zg')

    cctotal = cloud_overlap(Coarse.cc,
                            Coarse.zg,
                            cblev_res,
                            dem_geo,
                            windeffect,
                            levels)

    cctotal = change_data_storage(cctotal)

    Coarse.set('tcc')
    cc_coarse = resample_up(cctotal, Coarse.tcc, 4)
    bias = grid_calculator(cc_coarse, Coarse.tcc, '(a+0.001)/(b+0.001)')
    cc_fin = grid_calculatorX(cctotal, bias, 'a/b')
    Coarse.delete('tcc')

    return cc_fin


def solar_radiation(cc, Dem, year, month, day, hour):
    # calculate solar radiation
    Dem.set('demproj')
    Dem.set('dem_high')

    csr = clear_sky_solar_radiation(dem_merc=Dem.demproj,
                                    year=year,
                                    month=month,
                                    day=day,
                                    hour=hour)

    csr_latlong = proj_2_latlong(csr, Dem.dem_high)

    #Coarse.set('tcc')
    srad_sur = surface_radiation(csr_latlong,
                                 cc,
                                 'Surface Downwelling Shortwave Radiation')

    return srad_sur, csr_latlong


def relative_humidity(Coarse, Dem, windeffect):
    Coarse.set('rh')
    Coarse.set('zg')
    levels = range(0, 37)
    levels.reverse()
    Dem.set('dem_high')
    dem_geo = calc_geopotential(Dem.dem_high)

    rh1 = Multi_Level_to_Surface_Interpolation(var=Coarse.rh, zg=Coarse.zg, dem_geo=dem_geo, levels=levels)
    rh2 = grid_calculator_simple(rh1, 'log((a/100)/(1-(a/100)))')

    Dem.set('dem_low')
    windnorm = Grid_Normalization(windeffect)
    windnorm_coarse = resample_up(windnorm, Dem.dem_low, 4)

    rh3 = grid_calculator3(rh2, windnorm, windnorm_coarse, '(a*(b+(c-b)*(1-(c)))/c)')
    rh4 = grid_calculator_simple(rh3, '1/(1+exp(-1*(a)))')

    return rh4


def precipitation(wind_cor, wind_coarse, Coarse):
    Coarse.set('pr_')

    precip = downscale_precip(wind_cor,
                              wind_coarse,
                              Coarse.pr_,
                              'total surface precipitation', 3)

    return precip


def wind_speed_direction(Coarse, Dem):
    Coarse.set('vz')
    Coarse.set('uz')
    Coarse.set('zg')
    levels = range(0, 37)
    levels.reverse()
    Dem.set('dem_high')
    dem_geo = calc_geopotential(Dem.dem_high)

    u_sfc = Multi_Level_to_Surface_Interpolation(var=Coarse.uz, zg=Coarse.zg, dem_geo=dem_geo, levels=levels)
    v_sfc = Multi_Level_to_Surface_Interpolation(var=Coarse.vz, zg=Coarse.zg, dem_geo=dem_geo, levels=levels)

    dir, len = Gradient_Vector_from_Cartesian_to_Polar_Coordinates(u_sfc=u_sfc, v_sfc=v_sfc)

    return dir, len


def longwave_radiation_downwards(rsds, csr, hurs, tas):
    tas.Set_Scaling(0.1)
    # e_sat = grid_calculator_simple(tas, equ='0.6112*exp((17.62*a)/(243.12+a))')
    vp = grid_calculator(tas, hurs, equ='a*b')
    # sbc = Stefan Bolzman constant = 0.00000005670374
    # e_clear = 59.38 + 113.7 * (tas / 273.16)^6 + 96.96 * sqrt((4.65 * vpd) / (25 * tas))/sbc*T^4
    e_clear = grid_calculator(tas, vp, equ='59.38+113.7*(a/273.16)^6+96.96*sqrt((4.65*b)/(25*a))/(0.00000005670374*a^4)')
    t_atm = grid_calculator(rsds, csr, equ='a/b')
    # a =−0.84 and b = 0.84
    # e_eff = (1 + a * (1 - t_atm)) * e_clear + b * (1 - t_atm)
    e_eff = grid_calculator(t_atm, e_clear, equ='(1+(-0.84)*(1-a))*b+0.84*(1-a)')
    # lw = e_eff*sbc*tas^4
    lw = grid_calculator(e_eff, tas, equ='a*0.00000005670374*(b^4)')

    return lw

