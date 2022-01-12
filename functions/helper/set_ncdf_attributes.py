#!/usr/bin/env python

#This file is part of chelsa_highres.
#
#chelsa_highres is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#chelsa_highres is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with chelsa_highres.  If not, see <https://www.gnu.org/licenses/>.

import os

def set_ncdf_attributes(outfile, var, scale, offset, standard_name, longname, unit):
    os.system("ncrename -h -O -v Band1," + var + " " + outfile)
    os.system("ncatted -O -h -a add_offset," + var + ",o,f," + offset + " " + outfile)
    os.system("ncatted -O -h -a scale_factor," + var + ",o,f," + scale + " " + outfile)
    os.system("ncatted -O -h -a title,global,o,c,\"CHELSA-HIGHRES Very high resolution climate data \" " + outfile)
    os.system("ncatted -O -h -a institution,global,o,c,\"Swiss Federal Institute for Forest, Snow and Landscape Research (WSL)\" " + outfile)
    os.system("ncatted -O -h -a project,global,o,c,\"Climatologies at High Resolution for the Earth's Land Surface Areas (CHELSA)\" " + outfile)
    os.system("ncatted -O -h -a summary,global,o,c,\"ERA5 downscaled with the Climatologies at High resolution for the Earth's Land Surface Areas (CHELSA) method v2.0 addapted for very high resolutions\" " + outfile)
    os.system("ncatted -O -h -a standard_name," + var  + ",o,c,\"" + standard_name + "\" " + outfile)
    os.system("ncatted -O -h -a long_name," + var + ",o,c,\"" + longname + "\" " + outfile)
    os.system("ncatted -O -h -a units," + var + ",o,c,\"" + unit + "\" " + outfile)
    os.system("ncatted -O -h -a references,global,o,c,\"none\" " + outfile)
    os.system("ncatted -O -h -a downscaling_model,global,o,c,\"CHELSA v2.0\" " + outfile)
    os.system("ncatted -O -h -a forcing_model,global,o,c,\"ERA5\" " + outfile)
    os.system("ncatted -O -h -a contact,global,o,c,\"Dirk Karger <dirk.karger@wsl.ch> <https://chelsa-climate.org>\" " + outfile)
    os.system("ncatted -O -h -a Conventions,global,d,, " + outfile)
    os.system("ncatted -O -h -a history,global,d,, " + outfile)
    os.system("ncatted -O -h -a NCO,global,d,, " + outfile)
    os.system("ncatted -O -h -a history_of_appended_files,global,d,, " + outfile)

    return True

