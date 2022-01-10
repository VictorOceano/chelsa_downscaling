#!/usr/bin/env python

# This file is part of chelsa_isimip3b_ba_1km.
#
# chelsa_isimip3b_ba_1km is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# chelsa_isimip3b_ba_1km is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with chelsa_isimip3b_ba_1km.  If not, see <https://www.gnu.org/licenses/>.


from functions.saga_functions import *

Load_Tool_Libraries(True)


# change this that it accepts lat long

class Coarse_data:
    """ coarse grid data """

    def __init__(self, TEMP, lev_low=None, lev_high=None):
        self.tas_ = None
        self.tasmax = None
        self.tasmin = None
        self.u = None
        self.v = None
        self.hurs = None
        self.pr_ = None
        self.ps = None
        self.tcc = None
        self.rh = None
        self.zg = None
        self.cc = None
        self.tlapse_mean = None
        self.rsds = None
        self.TEMP = TEMP
        self.lev_low = lev_low
        self.lev_high = lev_high

    def set(self, var):
        if getattr(self, var) == None:
            return self._build_(var)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)

    def _delete_grid_list_(self, list):
        for m in range(0, list.Get_Item_Count() + 1):
            print('delete grid no:' + str(m))
            saga_api.SG_Get_Data_Manager().Delete(list.Get_Grid(m))
            list.Del_Items()

    def _build_(self, var):
        if var != 'tlapse_mean' and var != 'rsds':
            ds = import_ncdf(self.TEMP + var + '.nc').Get_Grid(0)
            setattr(self, var, ds)

        if var == 'zg' or var == 'cc' or var == 'rh':
            ds = import_ncdf(self.TEMP + var + '.nc')
            setattr(self, var, ds)

        if var == 'tlapse_mean':
            talow = import_ncdf(self.TEMP + 't.nc').Get_Grid(0)
            tahigh = import_ncdf(self.TEMP + 't.nc').Get_Grid(1)
            zglow = import_ncdf(self.TEMP + 'z.nc').Get_Grid(0)
            zghigh = import_ncdf(self.TEMP + 'z.nc').Get_Grid(1)
            zglow.Set_Scaling(zglow.Get_Scaling() * 0.10197162129)
            zghigh.Set_Scaling(zghigh.Get_Scaling() * 0.10197162129)
            tlapse_mean = tlapse(zglow, zghigh, talow, tahigh,
                                 '(c-d)/(b-a)')
            setattr(self, var, tlapse_mean)

            saga_api.SG_Get_Data_Manager().Delete(talow)
            saga_api.SG_Get_Data_Manager().Delete(tahigh)
            saga_api.SG_Get_Data_Manager().Delete(zglow)
            saga_api.SG_Get_Data_Manager().Delete(zghigh)
            #self.delete('talow')
            #self.delete('tahigh')
            #self.delete('zglow')
            #self.delete('zghigh')

        if var == 'rsds':
            rsds1 = import_ncdf(self.TEMP + 'rsds.nc')
            rsds = grid_calculator_simple(rsds1.Get_Grid(0), 'a/0.01157408333')
            setattr(self, var, rsds)
            self._delete_grid_list_(rsds1)
            # saga_api.SG_Get_Data_Manager().Delete_Unsaved()


class Dem_data:
    """ elevational grid data """

    def __init__(self, INPUT):
        self.demproj = None  # load_sagadata(INPUT + 'dem_merc3.sgrd')
        self.dem_latlong3 = None  # load_sagadata(INPUT + 'dem_latlong3.sgrd')
        self.dem_low = None  # load_sagadata(INPUT + 'orography.sgrd')
        self.dem_high = None  # load_sagadata(INPUT + 'dem_latlong.sgrd')
        self.INPUT = INPUT

    def set(self, var):
        if getattr(self, var) == None:
            return self._build_(var)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)

    def _delete_grid_list_(self, list):
        for m in range(0, list.Get_Item_Count() + 1):
            print('delete grid no:' + str(m))
            saga_api.SG_Get_Data_Manager().Delete(list.Get_Grid(m))
            list.Del_Items()

    def _build_(self, var):
        if var == 'demproj':
            ds = load_sagadata(self.INPUT + 'dem_merc.sgrd')
            setattr(self, var, ds)

        if var == 'dem_latlong3':
            ds = load_sagadata(self.INPUT + 'dem_latlong3.sgrd')
            setattr(self, var, ds)

        if var == 'dem_low':
            ds = load_sagadata(self.INPUT + 'orography.sgrd')
            setattr(self, var, ds)

        if var == 'dem_high':
            ds = load_sagadata(self.INPUT + 'dem_latlong.sgrd')
            setattr(self, var, ds)


class Aux_data:
    """ Auxillary grid data """

    def __init__(self, INPUT):
        self.patch = None  # load_sagadata(INPUT + 'patch.sgrd')
        self.expocor = None  # load_sagadata(INPUT + 'expocor.sgrd')
        self.dummy_W5E5 = None  # load_sagadata(INPUT + 'dummy_W5E5.sgrd')
        self.template_025 = None  # load_sagadata(W5E5 + 'template_025.sgrd')
        self.template_010 = None  # load_sagadata(W5E5 + 'template_010.sgrd')
        self.oceans = None  # load_sagadata(W5E5 + 'oceans.sgrd')
        self.continents = None  # load_sagadata(W5E5 + 'continents.sgrd')
        self.landseamask = None  # load_sagadata(W5E5 + 'landseamask.sgrd')
        self.INPUT = INPUT

    def set(self, var):
        if getattr(self, var) == None:
            return self._build_(var)

    def _build_(self, var):
        ds = load_sagadata(self.INPUT + var + '.sgrd')
        setattr(self, var, ds)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)





class Srad_data:
    """ cloud cover class """

    def __init__(self, SRAD, dayofyear):
        self.rsds_day = None  # import_gdal(SRAD + 'CHELSA_stot_pj_' + dayofyear + '_V.2.1.tif')
        self.SRAD = SRAD
        self.dayofyear = dayofyear

    def set(self, var):
        if getattr(self, var) == None:
            return self._build_(var)

    def delete(self, var):
        saga_api.SG_Get_Data_Manager().Delete(getattr(self, var))
        setattr(self, var, None)

    def _build_(self, var):
        ds = import_gdal(self.SRAD + 'CHELSA_stot_pj_' + self.dayofyear + '_V.2.1.tif')
        setattr(self, var, ds)




















