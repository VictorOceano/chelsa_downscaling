
from functions.saga_functions import tlapse
from functions.saga_functions import import_ncdf
from functions.get_era import get_era_via_api
from functions.saga_functions import change_latlong
import saga_api

year = 1980
month = 12
day = 30
hour = 11
tmp = '/home/karger/scratch/'

era_data = get_era_via_api(year=year,
                   month=month,
                   day=day,
                   hour=hour,
                   tmp=tmp)


class Lapse_rate(year, month, day, hour, tmp):
    def __init__(self):
        self.t = get_era_via_api(year=year,
                          month=month,
                          day=day,
                          hour=hour,
                          tmp=tmp).t()
        self.z = get_era_via_api(year=year,
                          month=month,
                          day=day,
                          hour=hour,
                          tmp=tmp).z()
        self.times = [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00'
        ]

    def calc_lapserate(self):
        self.t()
        self.z()
        filename = tmp + 't.nc'
        tlevels  = import_ncdf(filename)
        filename = tmp + 'z.nc'
        zlevels  = import_ncdf(filename)
        zlevels.Get_Grid(0).Set_Scaling(zlevels.Get_Grid(0).Get_Scaling() * 0.10197162129)
        zlevels.Get_Grid(1).Set_Scaling(zlevels.Get_Grid(1).Get_Scaling() * 0.10197162129)
        tz = tlapse(zlevels.Get_Grid(0), zlevels.Get_Grid(1), tlevels.Get_Grid(0), tlevels.Get_Grid(1), '(d-c)/(b-a)')
        tz1 = change_latlong(tz)
        tz1.Get_Projection().Create(saga_api.CSG_String('+proj=longlat +datum=WGS84 +no_defs'), saga_api.SG_PROJ_FMT_Proj4)

        return tz


lz = Lapse_rate()


era_data.t()
era_data.z()

if __name__ == '__main__':
    saga_api.SG_Get_Data_Manager().Delete_All()  #
    Load_Tool_Libraries(True)
    

