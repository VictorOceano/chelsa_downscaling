
from functions.saga_functions import *
from functions.get_era import *

year = 1980
month = 12
day = 30
hour = 11
tmp = '/home/karger/scratch/'

era_data = get_era(year=year,
                   month=month,
                   day=day,
                   hour=hour,
                   tmp=tmp)



class Lapse_rate():
    def __init__(self):
        era_data.__init__(self,year=year,
                          month=month,
                          day=day,
                          hour=hour,
                          tmp=tm)

    def calc_lapserate:
        self.t()
        self.z()
        filename = TEMP + 't_levels_' + times[int(hour)] + '.nc'
        tlevels  = import_ncdf(filename)
        filename = TEMP + 'z_levels_' + times[int(hour)] + '.nc'
        zlevels  = import_ncdf(filename)
        zlevels.Get_Grid(0).Set_Scaling(zlevels.Get_Grid(0).Get_Scaling() * 0.10197162129)
        zlevels.Get_Grid(1).Set_Scaling(zlevels.Get_Grid(1).Get_Scaling() * 0.10197162129)
        tz  = tlapse(zlevels.Get_Grid(0), zlevels.Get_Grid(1), tlevels.Get_Grid(0), tlevels.Get_Grid(1), '(d-c)/(b-a)')
        tz1 = change_latlong(tz)
        tz1.Get_Projection().Create(saga_api.CSG_String('+proj=longlat +datum=WGS84 +no_defs'), saga_api.SG_PROJ_FMT_Proj4)

        return tz





era_data.t()
era_data.z()

if __name__ == '__main__':
    saga_api.SG_Get_Data_Manager().Delete_All()  #
    Load_Tool_Libraries(True)
    

